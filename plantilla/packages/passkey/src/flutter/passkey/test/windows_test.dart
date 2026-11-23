import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:passkey/passkey.dart';

// On Windows, Dart writes clientDataJSON and the response; the channel
// answers here what the API of Windows would.
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final calls = <MethodCall>[];

  setUp(() {
    calls.clear();
    TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger.setMockMethodCallHandler(
      const MethodChannel('passkey'),
      (call) async {
        calls.add(call);
        if (call.method == 'get') {
          return {
            'credentialId': Uint8List.fromList([1, 2, 3]),
            'authenticatorData': Uint8List.fromList([4, 5]),
            'signature': Uint8List.fromList([6]),
            'userHandle': Uint8List.fromList([7, 8, 9, 10]),
          };
        }
        throw PlatformException(code: 'cancelled', message: 'closed');
      },
    );
  });

  test('get signs the client data of the RP ID and answers WebAuthn JSON', () async {
    final options = jsonEncode({
      'challenge': 'AAEC',
      'rpId': 'example.com',
      'allowCredentials': [
        {'type': 'public-key', 'id': 'AQID', 'transports': <String>[]},
      ],
      'userVerification': 'preferred',
    });
    final response = jsonDecode(await getPasskey(options)) as Map<String, Object?>;
    final arguments = calls.single.arguments as Map<Object?, Object?>;
    expect(arguments['rpId'], 'example.com');
    expect(arguments['allowCredentials'], [
      Uint8List.fromList([1, 2, 3]),
    ]);
    final clientData = utf8.decode(arguments['clientData']! as Uint8List);
    expect(jsonDecode(clientData), {
      'type': 'webauthn.get',
      'challenge': 'AAEC',
      'origin': 'https://example.com',
      'crossOrigin': false,
    });
    expect(response['id'], 'AQID');
    expect(response['rawId'], 'AQID');
    expect(response['clientExtensionResults'], <String, Object?>{});
    final body = response['response']! as Map<String, Object?>;
    expect(
      utf8.decode(base64Url.decode(base64Url.normalize(body['clientDataJSON']! as String))),
      clientData,
    );
    expect(body['authenticatorData'], 'BAU');
    expect(body['signature'], 'Bg');
    expect(body['userHandle'], 'BwgJCg');
  }, skip: !Platform.isWindows);

  test('a cancel of the system is a PasskeyException', () async {
    final options = jsonEncode({
      'challenge': 'AAEC',
      'rp': {'id': 'example.com', 'name': 'example.com'},
      'user': {'id': 'AQ', 'name': 'ana@example.com', 'displayName': ''},
      'pubKeyCredParams': [
        {'type': 'public-key', 'alg': -7},
      ],
    });
    expect(
      createPasskey(options),
      throwsA(
        isA<PasskeyException>().having((e) => e.failure, 'failure', PasskeyFailure.cancelled),
      ),
    );
  });
}

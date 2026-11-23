import 'package:flet/flet.dart';
import 'package:passkey/passkey.dart';

class PasskeyService extends FletService {
  PasskeyService({required super.control});

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_invokeMethod);
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    final options = (args as Map)["options"] as String;
    switch (name) {
      case "get":
        return getPasskey(options);
      case "create":
        return createPasskey(options);
      default:
        throw Exception("Unknown Passkey method: $name");
    }
  }

  @override
  void dispose() {
    control.removeInvokeMethodListener(_invokeMethod);
    super.dispose();
  }
}

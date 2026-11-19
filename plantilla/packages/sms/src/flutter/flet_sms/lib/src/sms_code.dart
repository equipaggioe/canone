import 'dart:async';

import 'package:flet/flet.dart';
import 'package:smart_auth/smart_auth.dart';

// The code follows the "#" of the last line, as autenticacion.md writes it.
const _code = r'(?<=#)\d{6}';

class SmsCodeService extends FletService {
  SmsCodeService({required super.control});

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_invokeMethod);
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    switch (name) {
      case "listen":
        unawaited(_wait());
        return null;
      case "stop":
        await SmartAuth.instance.removeSmsRetrieverApiListener();
        return null;
      case "signature":
        final result = await SmartAuth.instance.getAppSignature();
        if (!result.hasData) throw Exception("No app signature: ${result.error}");
        return result.data;
      default:
        throw Exception("Unknown SmsCode method: $name");
    }
  }

  Future<void> _wait() async {
    final result = await SmartAuth.instance.getSmsWithRetrieverApi(matcher: _code);
    final code = result.data?.code;
    if (code != null) control.triggerEvent("code", {"code": code});
  }

  @override
  void dispose() {
    control.removeInvokeMethodListener(_invokeMethod);
    unawaited(SmartAuth.instance.removeSmsRetrieverApiListener());
    super.dispose();
  }
}

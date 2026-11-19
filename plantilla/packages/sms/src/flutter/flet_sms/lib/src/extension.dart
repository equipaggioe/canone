import 'package:flet/flet.dart';

import 'sms_code.dart';

class Extension extends FletExtension {
  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "SmsCode":
        return SmsCodeService(control: control);
      default:
        return null;
    }
  }
}

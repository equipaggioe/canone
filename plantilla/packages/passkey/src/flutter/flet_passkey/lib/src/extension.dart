import 'package:flet/flet.dart';

import 'passkey_service.dart';

class Extension extends FletExtension {
  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "Passkey":
        return PasskeyService(control: control);
      default:
        return null;
    }
  }
}

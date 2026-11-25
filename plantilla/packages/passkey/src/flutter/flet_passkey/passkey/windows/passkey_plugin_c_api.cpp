#include "include/passkey/passkey_plugin_c_api.h"

#include <flutter/plugin_registrar_windows.h>

#include "passkey_plugin.h"

void PasskeyPluginCApiRegisterWithRegistrar(
    FlutterDesktopPluginRegistrarRef registrar) {
  passkey::PasskeyPlugin::RegisterWithRegistrar(
      flutter::PluginRegistrarManager::GetInstance()
          ->GetRegistrar<flutter::PluginRegistrarWindows>(registrar));
}

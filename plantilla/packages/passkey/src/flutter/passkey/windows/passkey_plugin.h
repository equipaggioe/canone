#ifndef FLUTTER_PLUGIN_PASSKEY_PLUGIN_H_
#define FLUTTER_PLUGIN_PASSKEY_PLUGIN_H_

#include <flutter/encodable_value.h>
#include <flutter/method_channel.h>
#include <flutter/plugin_registrar_windows.h>

#include <memory>

namespace passkey {

// Runs the ceremonies of WebAuthn with the API of Windows, over the window
// of the app. Dart writes clientDataJSON and the JSON of the response.
class PasskeyPlugin : public flutter::Plugin {
 public:
  using Result = std::unique_ptr<flutter::MethodResult<flutter::EncodableValue>>;

  static void RegisterWithRegistrar(flutter::PluginRegistrarWindows *registrar);

  explicit PasskeyPlugin(flutter::PluginRegistrarWindows *registrar);

  virtual ~PasskeyPlugin();

  PasskeyPlugin(const PasskeyPlugin &) = delete;
  PasskeyPlugin &operator=(const PasskeyPlugin &) = delete;

  void HandleMethodCall(const flutter::MethodCall<flutter::EncodableValue> &method_call,
                        Result result);

 private:
  void Get(const flutter::EncodableMap &args, Result result);
  void Create(const flutter::EncodableMap &args, Result result);

  flutter::PluginRegistrarWindows *registrar_;
};

}  // namespace passkey

#endif  // FLUTTER_PLUGIN_PASSKEY_PLUGIN_H_

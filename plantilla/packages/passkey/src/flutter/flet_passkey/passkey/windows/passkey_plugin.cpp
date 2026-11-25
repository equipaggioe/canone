#include "passkey_plugin.h"

// This must be included before many other Windows headers.
#include <windows.h>

#include <webauthn.h>

#include <flutter/method_channel.h>
#include <flutter/plugin_registrar_windows.h>
#include <flutter/standard_method_codec.h>

#include <memory>
#include <string>
#include <variant>
#include <vector>

namespace passkey {

namespace {

using flutter::EncodableList;
using flutter::EncodableMap;
using flutter::EncodableValue;
using Bytes = std::vector<uint8_t>;

// Guidance for the dialog of Windows, which may keep it open longer.
constexpr DWORD kTimeout = 5 * 60 * 1000;

const EncodableValue &Field(const EncodableMap &map, const char *key) {
  return map.at(EncodableValue(key));
}

std::string Text(const EncodableMap &map, const char *key) {
  return std::get<std::string>(Field(map, key));
}

Bytes Data(const EncodableMap &map, const char *key) {
  return std::get<Bytes>(Field(map, key));
}

std::vector<Bytes> Ids(const EncodableMap &map, const char *key) {
  std::vector<Bytes> ids;
  for (const auto &id : std::get<EncodableList>(Field(map, key))) {
    ids.push_back(std::get<Bytes>(id));
  }
  return ids;
}

std::wstring Wide(const std::string &text) {
  if (text.empty()) {
    return std::wstring();
  }
  int size = MultiByteToWideChar(CP_UTF8, 0, text.data(), static_cast<int>(text.size()), nullptr, 0);
  std::wstring wide(size, L'\0');
  MultiByteToWideChar(CP_UTF8, 0, text.data(), static_cast<int>(text.size()), wide.data(), size);
  return wide;
}

std::string Narrow(const std::wstring &text) {
  if (text.empty()) {
    return std::string();
  }
  int size = WideCharToMultiByte(CP_UTF8, 0, text.data(), static_cast<int>(text.size()), nullptr, 0,
                                 nullptr, nullptr);
  std::string narrow(size, '\0');
  WideCharToMultiByte(CP_UTF8, 0, text.data(), static_cast<int>(text.size()), narrow.data(), size,
                      nullptr, nullptr);
  return narrow;
}

EncodableValue Copy(const BYTE *data, DWORD size) {
  return EncodableValue(Bytes(data, data + size));
}

DWORD Verification(const std::string &value) {
  if (value == "required") {
    return WEBAUTHN_USER_VERIFICATION_REQUIREMENT_REQUIRED;
  }
  if (value == "discouraged") {
    return WEBAUTHN_USER_VERIFICATION_REQUIREMENT_DISCOURAGED;
  }
  return WEBAUTHN_USER_VERIFICATION_REQUIREMENT_PREFERRED;
}

// The descriptors point into ids, which must outlive them.
std::vector<WEBAUTHN_CREDENTIAL> Descriptors(std::vector<Bytes> &ids) {
  std::vector<WEBAUTHN_CREDENTIAL> list;
  for (auto &id : ids) {
    list.push_back({WEBAUTHN_CREDENTIAL_CURRENT_VERSION, static_cast<DWORD>(id.size()), id.data(),
                    WEBAUTHN_CREDENTIAL_TYPE_PUBLIC_KEY});
  }
  return list;
}

// The names are those of PasskeyFailure in Dart.
std::string Failure(HRESULT hr) {
  if (hr == NTE_USER_CANCELLED) {
    return "cancelled";
  }
  if (hr == NTE_NOT_FOUND) {
    return "noCredential";
  }
  if (hr == NTE_NOT_SUPPORTED) {
    return "unsupported";
  }
  return "failed";
}

EncodableList Transports(DWORD used) {
  EncodableList names;
  const std::pair<DWORD, const char *> known[] = {
      {WEBAUTHN_CTAP_TRANSPORT_USB, WEBAUTHN_CTAP_TRANSPORT_USB_STRING},
      {WEBAUTHN_CTAP_TRANSPORT_NFC, WEBAUTHN_CTAP_TRANSPORT_NFC_STRING},
      {WEBAUTHN_CTAP_TRANSPORT_BLE, WEBAUTHN_CTAP_TRANSPORT_BLE_STRING},
      {WEBAUTHN_CTAP_TRANSPORT_INTERNAL, WEBAUTHN_CTAP_TRANSPORT_INTERNAL_STRING},
      {WEBAUTHN_CTAP_TRANSPORT_HYBRID, WEBAUTHN_CTAP_TRANSPORT_HYBRID_STRING},
      {WEBAUTHN_CTAP_TRANSPORT_SMART_CARD, WEBAUTHN_CTAP_TRANSPORT_SMART_CARD_STRING},
  };
  for (const auto &[flag, name] : known) {
    if (used & flag) {
      names.push_back(EncodableValue(name));
    }
  }
  return names;
}

}  // namespace

// static
void PasskeyPlugin::RegisterWithRegistrar(flutter::PluginRegistrarWindows *registrar) {
  auto channel = std::make_unique<flutter::MethodChannel<EncodableValue>>(
      registrar->messenger(), "passkey", &flutter::StandardMethodCodec::GetInstance());
  auto plugin = std::make_unique<PasskeyPlugin>(registrar);
  channel->SetMethodCallHandler([plugin_pointer = plugin.get()](const auto &call, auto result) {
    plugin_pointer->HandleMethodCall(call, std::move(result));
  });
  registrar->AddPlugin(std::move(plugin));
}

PasskeyPlugin::PasskeyPlugin(flutter::PluginRegistrarWindows *registrar)
    : registrar_(registrar) {}

PasskeyPlugin::~PasskeyPlugin() {}

void PasskeyPlugin::HandleMethodCall(const flutter::MethodCall<EncodableValue> &method_call,
                                     Result result) {
  const auto *args = std::get_if<EncodableMap>(method_call.arguments());
  if (args == nullptr) {
    result->Error("failed", "The arguments are not a map");
    return;
  }
  try {
    if (method_call.method_name() == "get") {
      Get(*args, std::move(result));
    } else if (method_call.method_name() == "create") {
      Create(*args, std::move(result));
    } else {
      result->NotImplemented();
    }
  } catch (const std::exception &error) {
    result->Error("failed", error.what());
  }
}

// The call is modal: Windows shows its dialog over the window of the app,
// and the platform thread waits for it.
void PasskeyPlugin::Get(const EncodableMap &args, Result result) {
  std::wstring rp_id = Wide(Text(args, "rpId"));
  Bytes client_data = Data(args, "clientData");
  std::vector<Bytes> ids = Ids(args, "allowCredentials");
  std::vector<WEBAUTHN_CREDENTIAL> allowed = Descriptors(ids);

  WEBAUTHN_CLIENT_DATA data = {WEBAUTHN_CLIENT_DATA_CURRENT_VERSION,
                               static_cast<DWORD>(client_data.size()), client_data.data(),
                               WEBAUTHN_HASH_ALGORITHM_SHA_256};
  // The first version of the options: every Windows with the API reads it.
  WEBAUTHN_AUTHENTICATOR_GET_ASSERTION_OPTIONS options = {};
  options.dwVersion = WEBAUTHN_AUTHENTICATOR_GET_ASSERTION_OPTIONS_VERSION_1;
  options.dwTimeoutMilliseconds = kTimeout;
  options.CredentialList = {static_cast<DWORD>(allowed.size()), allowed.data()};
  options.dwAuthenticatorAttachment = WEBAUTHN_AUTHENTICATOR_ATTACHMENT_ANY;
  options.dwUserVerificationRequirement = Verification(Text(args, "userVerification"));

  HWND window = GetAncestor(registrar_->GetView()->GetNativeWindow(), GA_ROOT);
  PWEBAUTHN_ASSERTION assertion = nullptr;
  HRESULT hr = WebAuthNAuthenticatorGetAssertion(window, rp_id.c_str(), &data, &options, &assertion);
  if (FAILED(hr)) {
    result->Error(Failure(hr), Narrow(WebAuthNGetErrorName(hr)));
    return;
  }
  EncodableMap response = {
      {EncodableValue("credentialId"),
       Copy(assertion->Credential.pbId, assertion->Credential.cbId)},
      {EncodableValue("authenticatorData"),
       Copy(assertion->pbAuthenticatorData, assertion->cbAuthenticatorData)},
      {EncodableValue("signature"), Copy(assertion->pbSignature, assertion->cbSignature)},
      {EncodableValue("userHandle"), Copy(assertion->pbUserId, assertion->cbUserId)},
  };
  WebAuthNFreeAssertion(assertion);
  result->Success(EncodableValue(response));
}

void PasskeyPlugin::Create(const EncodableMap &args, Result result) {
  std::wstring rp_id = Wide(Text(args, "rpId"));
  std::wstring rp_name = Wide(Text(args, "rpName"));
  std::wstring user_name = Wide(Text(args, "userName"));
  std::wstring display_name = Wide(Text(args, "userDisplayName"));
  Bytes user_id = Data(args, "userId");
  Bytes client_data = Data(args, "clientData");
  std::vector<Bytes> ids = Ids(args, "excludeCredentials");
  std::vector<WEBAUTHN_CREDENTIAL> excluded = Descriptors(ids);

  WEBAUTHN_RP_ENTITY_INFORMATION rp = {WEBAUTHN_RP_ENTITY_INFORMATION_CURRENT_VERSION,
                                       rp_id.c_str(), rp_name.c_str(), nullptr};
  WEBAUTHN_USER_ENTITY_INFORMATION user = {WEBAUTHN_USER_ENTITY_INFORMATION_CURRENT_VERSION,
                                           static_cast<DWORD>(user_id.size()), user_id.data(),
                                           user_name.c_str(), nullptr, display_name.c_str()};
  std::vector<WEBAUTHN_COSE_CREDENTIAL_PARAMETER> parameters;
  for (const auto &algorithm : std::get<EncodableList>(Field(args, "algorithms"))) {
    parameters.push_back({WEBAUTHN_COSE_CREDENTIAL_PARAMETER_CURRENT_VERSION,
                          WEBAUTHN_CREDENTIAL_TYPE_PUBLIC_KEY, std::get<int32_t>(algorithm)});
  }
  WEBAUTHN_COSE_CREDENTIAL_PARAMETERS algorithms = {static_cast<DWORD>(parameters.size()),
                                                    parameters.data()};
  WEBAUTHN_CLIENT_DATA data = {WEBAUTHN_CLIENT_DATA_CURRENT_VERSION,
                               static_cast<DWORD>(client_data.size()), client_data.data(),
                               WEBAUTHN_HASH_ALGORITHM_SHA_256};
  WEBAUTHN_AUTHENTICATOR_MAKE_CREDENTIAL_OPTIONS options = {};
  options.dwVersion = WEBAUTHN_AUTHENTICATOR_MAKE_CREDENTIAL_OPTIONS_VERSION_1;
  options.dwTimeoutMilliseconds = kTimeout;
  options.CredentialList = {static_cast<DWORD>(excluded.size()), excluded.data()};
  options.dwAuthenticatorAttachment = WEBAUTHN_AUTHENTICATOR_ATTACHMENT_ANY;
  // autenticacion.md: every passkey is discoverable, without attestation.
  options.bRequireResidentKey = TRUE;
  options.dwUserVerificationRequirement = Verification(Text(args, "userVerification"));
  options.dwAttestationConveyancePreference = WEBAUTHN_ATTESTATION_CONVEYANCE_PREFERENCE_NONE;

  HWND window = GetAncestor(registrar_->GetView()->GetNativeWindow(), GA_ROOT);
  PWEBAUTHN_CREDENTIAL_ATTESTATION attestation = nullptr;
  HRESULT hr = WebAuthNAuthenticatorMakeCredential(window, &rp, &user, &algorithms, &data, &options,
                                                   &attestation);
  if (FAILED(hr)) {
    result->Error(Failure(hr), Narrow(WebAuthNGetErrorName(hr)));
    return;
  }
  // The transport came with the third version of the attestation: an
  // older Windows reports none.
  DWORD used = attestation->dwVersion >= WEBAUTHN_CREDENTIAL_ATTESTATION_VERSION_3
                   ? attestation->dwUsedTransport
                   : 0;
  EncodableMap response = {
      {EncodableValue("credentialId"),
       Copy(attestation->pbCredentialId, attestation->cbCredentialId)},
      {EncodableValue("attestationObject"),
       Copy(attestation->pbAttestationObject, attestation->cbAttestationObject)},
      {EncodableValue("transports"), EncodableValue(Transports(used))},
  };
  WebAuthNFreeCredentialAttestation(attestation);
  result->Success(EncodableValue(response));
}

}  // namespace passkey

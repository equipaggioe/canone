import AuthenticationServices
import Flutter
import UIKit

/// Runs the ceremonies of WebAuthn with AuthenticationServices, over the app.
///
/// It reads the options of WebAuthn and writes the response as the JSON
/// that the browser gives, with the binary fields in base64url.
public class PasskeyPlugin: NSObject, FlutterPlugin {
  private var ceremony: Ceremony?

  public static func register(with registrar: FlutterPluginRegistrar) {
    let channel = FlutterMethodChannel(name: "passkey", binaryMessenger: registrar.messenger())
    registrar.addMethodCallDelegate(PasskeyPlugin(), channel: channel)
  }

  public func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
    guard let text = call.arguments as? String,
      let options = try? JSONSerialization.jsonObject(with: Data(text.utf8)) as? [String: Any]
    else {
      result(FlutterError(code: "failed", message: "The options are not a JSON object", details: nil))
      return
    }
    do {
      let request: ASAuthorizationRequest
      switch call.method {
      case "get":
        request = try assertionRequest(options)
      case "create":
        request = try registrationRequest(options)
      default:
        result(FlutterMethodNotImplemented)
        return
      }
      let ceremony = Ceremony(result: result) { [weak self] in self?.ceremony = nil }
      self.ceremony = ceremony
      ceremony.perform(request)
    } catch let error as OptionError {
      result(FlutterError(code: "failed", message: error.message, details: nil))
    } catch {
      result(FlutterError(code: "failed", message: "\(error)", details: nil))
    }
  }
}

struct OptionError: Error {
  let message: String
}

func string(_ options: [String: Any], _ key: String) throws -> String {
  guard let value = options[key] as? String else {
    throw OptionError(message: "The options have no \(key)")
  }
  return value
}

func bytes(_ options: [String: Any], _ key: String) throws -> Data {
  guard let value = Data(base64URL: try string(options, key)) else {
    throw OptionError(message: "\(key) is not base64url")
  }
  return value
}

func descriptors(_ options: [String: Any], _ key: String) throws -> [Data] {
  let list = options[key] as? [[String: Any]] ?? []
  return try list.map { try bytes($0, "id") }
}

func preference(_ options: [String: Any]) -> ASAuthorizationPublicKeyCredentialUserVerificationPreference {
  ASAuthorizationPublicKeyCredentialUserVerificationPreference(
    rawValue: options["userVerification"] as? String ?? "preferred")
}

func assertionRequest(_ options: [String: Any]) throws -> ASAuthorizationRequest {
  let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
    relyingPartyIdentifier: try string(options, "rpId"))
  let request = provider.createCredentialAssertionRequest(challenge: try bytes(options, "challenge"))
  request.allowedCredentials = try descriptors(options, "allowCredentials").map {
    ASAuthorizationPlatformPublicKeyCredentialDescriptor(credentialID: $0)
  }
  request.userVerificationPreference = preference(options)
  return request
}

func registrationRequest(_ options: [String: Any]) throws -> ASAuthorizationRequest {
  guard let rp = options["rp"] as? [String: Any], let user = options["user"] as? [String: Any]
  else {
    throw OptionError(message: "The options have no rp or user")
  }
  let provider = ASAuthorizationPlatformPublicKeyCredentialProvider(
    relyingPartyIdentifier: try string(rp, "id"))
  let request = provider.createCredentialRegistrationRequest(
    challenge: try bytes(options, "challenge"), name: try string(user, "name"),
    userID: try bytes(user, "id"))
  request.attestationPreference = .none
  request.userVerificationPreference = preference(
    options["authenticatorSelection"] as? [String: Any] ?? [:])
  if #available(iOS 17.4, *) {
    request.excludedCredentials = try descriptors(options, "excludeCredentials").map {
      ASAuthorizationPlatformPublicKeyCredentialDescriptor(credentialID: $0)
    }
  }
  return request
}

/// One ceremony: it keeps its controller alive until the system answers.
final class Ceremony: NSObject, ASAuthorizationControllerDelegate,
  ASAuthorizationControllerPresentationContextProviding
{
  private let result: FlutterResult
  private let done: () -> Void

  init(result: @escaping FlutterResult, done: @escaping () -> Void) {
    self.result = result
    self.done = done
  }

  func perform(_ request: ASAuthorizationRequest) {
    let controller = ASAuthorizationController(authorizationRequests: [request])
    controller.delegate = self
    controller.presentationContextProvider = self
    controller.performRequests()
  }

  func presentationAnchor(for controller: ASAuthorizationController) -> ASPresentationAnchor {
    let scenes = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }
    return scenes.flatMap(\.windows).first(where: \.isKeyWindow) ?? ASPresentationAnchor()
  }

  func authorizationController(
    controller: ASAuthorizationController,
    didCompleteWithAuthorization authorization: ASAuthorization
  ) {
    defer { done() }
    let credential = authorization.credential
    var response: [String: Any]
    if let assertion = credential as? ASAuthorizationPlatformPublicKeyCredentialAssertion {
      response = [
        "clientDataJSON": assertion.rawClientDataJSON.base64URL,
        "authenticatorData": assertion.rawAuthenticatorData.base64URL,
        "signature": assertion.signature.base64URL,
        "userHandle": assertion.userID.base64URL,
      ]
    } else if let registration = credential
      as? ASAuthorizationPlatformPublicKeyCredentialRegistration,
      let attestation = registration.rawAttestationObject
    {
      // A passkey of the platform syncs: it is used here and from a phone nearby.
      response = [
        "clientDataJSON": registration.rawClientDataJSON.base64URL,
        "attestationObject": attestation.base64URL,
        "transports": ["hybrid", "internal"],
      ]
    } else {
      result(FlutterError(code: "failed", message: "Not a passkey", details: nil))
      return
    }
    let id = (credential as? ASPublicKeyCredential)?.credentialID.base64URL ?? ""
    let body: [String: Any] = [
      "id": id,
      "rawId": id,
      "type": "public-key",
      "response": response,
      "clientExtensionResults": [String: Any](),
      "authenticatorAttachment": "platform",
    ]
    guard let data = try? JSONSerialization.data(withJSONObject: body),
      let text = String(data: data, encoding: .utf8)
    else {
      result(FlutterError(code: "failed", message: "The response is not JSON", details: nil))
      return
    }
    result(text)
  }

  func authorizationController(
    controller: ASAuthorizationController, didCompleteWithError error: Error
  ) {
    defer { done() }
    let code: String
    switch (error as? ASAuthorizationError)?.code {
    case .canceled:
      code = "cancelled"
    case .notHandled:
      code = "noCredential"
    default:
      code = "failed"
    }
    result(FlutterError(code: code, message: error.localizedDescription, details: nil))
  }
}

extension Data {
  init?(base64URL text: String) {
    var base64 = text.replacingOccurrences(of: "-", with: "+").replacingOccurrences(of: "_", with: "/")
    base64 += String(repeating: "=", count: (4 - base64.count % 4) % 4)
    self.init(base64Encoded: base64)
  }

  var base64URL: String {
    base64EncodedString().replacingOccurrences(of: "+", with: "-")
      .replacingOccurrences(of: "/", with: "_").replacingOccurrences(of: "=", with: "")
  }
}

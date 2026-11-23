package canone.passkey

import android.app.Activity
import androidx.credentials.CreateCredentialResponse
import androidx.credentials.CreatePublicKeyCredentialRequest
import androidx.credentials.CreatePublicKeyCredentialResponse
import androidx.credentials.CredentialManager
import androidx.credentials.CredentialManagerCallback
import androidx.credentials.GetCredentialRequest
import androidx.credentials.GetCredentialResponse
import androidx.credentials.GetPublicKeyCredentialOption
import androidx.credentials.PublicKeyCredential
import androidx.credentials.exceptions.CreateCredentialCancellationException
import androidx.credentials.exceptions.CreateCredentialException
import androidx.credentials.exceptions.CreateCredentialNoCreateOptionException
import androidx.credentials.exceptions.CreateCredentialProviderConfigurationException
import androidx.credentials.exceptions.CreateCredentialUnsupportedException
import androidx.credentials.exceptions.GetCredentialCancellationException
import androidx.credentials.exceptions.GetCredentialException
import androidx.credentials.exceptions.GetCredentialProviderConfigurationException
import androidx.credentials.exceptions.GetCredentialUnsupportedException
import androidx.credentials.exceptions.NoCredentialException
import io.flutter.embedding.engine.plugins.FlutterPlugin
import io.flutter.embedding.engine.plugins.activity.ActivityAware
import io.flutter.embedding.engine.plugins.activity.ActivityPluginBinding
import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import io.flutter.plugin.common.MethodChannel.MethodCallHandler
import io.flutter.plugin.common.MethodChannel.Result

/** Runs the ceremonies of WebAuthn with Credential Manager, over the app. */
class PasskeyPlugin :
    FlutterPlugin,
    ActivityAware,
    MethodCallHandler {
    private lateinit var channel: MethodChannel

    // Credential Manager shows its sheet over the activity in the foreground.
    private var activity: Activity? = null

    override fun onAttachedToEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel = MethodChannel(binding.binaryMessenger, "passkey")
        channel.setMethodCallHandler(this)
    }

    override fun onDetachedFromEngine(binding: FlutterPlugin.FlutterPluginBinding) {
        channel.setMethodCallHandler(null)
    }

    override fun onAttachedToActivity(binding: ActivityPluginBinding) {
        activity = binding.activity
    }

    override fun onDetachedFromActivityForConfigChanges() {
        activity = null
    }

    override fun onReattachedToActivityForConfigChanges(binding: ActivityPluginBinding) {
        activity = binding.activity
    }

    override fun onDetachedFromActivity() {
        activity = null
    }

    override fun onMethodCall(
        call: MethodCall,
        result: Result,
    ) {
        val current = activity
        val options = call.arguments as? String
        when {
            current == null -> result.error("failed", "No activity in the foreground", null)
            options == null -> result.error("failed", "The options are not a string", null)
            call.method == "get" -> get(current, options, result)
            call.method == "create" -> create(current, options, result)
            else -> result.notImplemented()
        }
    }

    private fun get(
        activity: Activity,
        options: String,
        result: Result,
    ) {
        val request = GetCredentialRequest(listOf(GetPublicKeyCredentialOption(options)))
        CredentialManager.create(activity).getCredentialAsync(
            activity,
            request,
            null,
            activity.mainExecutor,
            object : CredentialManagerCallback<GetCredentialResponse, GetCredentialException> {
                override fun onResult(response: GetCredentialResponse) {
                    val credential = response.credential
                    if (credential is PublicKeyCredential) {
                        result.success(credential.authenticationResponseJson)
                    } else {
                        result.error("failed", "Not a passkey: ${credential.type}", null)
                    }
                }

                override fun onError(e: GetCredentialException) {
                    result.error(failure(e), e.message, null)
                }
            },
        )
    }

    private fun create(
        activity: Activity,
        options: String,
        result: Result,
    ) {
        CredentialManager.create(activity).createCredentialAsync(
            activity,
            CreatePublicKeyCredentialRequest(options),
            null,
            activity.mainExecutor,
            object : CredentialManagerCallback<CreateCredentialResponse, CreateCredentialException> {
                override fun onResult(response: CreateCredentialResponse) {
                    if (response is CreatePublicKeyCredentialResponse) {
                        result.success(response.registrationResponseJson)
                    } else {
                        result.error("failed", "Not a passkey: ${response.type}", null)
                    }
                }

                override fun onError(e: CreateCredentialException) {
                    result.error(failure(e), e.message, null)
                }
            },
        )
    }
}

// android.md: each subclass of the exception is handled apart; the names
// are those of PasskeyFailure in Dart.
private fun failure(e: GetCredentialException): String =
    when (e) {
        is GetCredentialCancellationException -> "cancelled"
        is NoCredentialException -> "noCredential"
        is GetCredentialUnsupportedException, is GetCredentialProviderConfigurationException -> "unsupported"
        else -> "failed"
    }

private fun failure(e: CreateCredentialException): String =
    when (e) {
        is CreateCredentialCancellationException -> "cancelled"
        is CreateCredentialNoCreateOptionException -> "noCredential"
        is CreateCredentialUnsupportedException, is CreateCredentialProviderConfigurationException -> "unsupported"
        else -> "failed"
    }

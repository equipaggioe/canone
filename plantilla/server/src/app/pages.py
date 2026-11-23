"""The pages the server shows: they load nothing from other sites."""

from gettext import GNUTranslations
from html import escape

STYLE = """
:root { color-scheme: light dark; font-family: system-ui, sans-serif; }
body { display: grid; place-items: center; min-height: 100vh; margin: 0; padding: 16px; }
main { display: grid; gap: 16px; max-width: 360px; text-align: center; }
button { min-height: 48px; font: inherit; padding: 0 24px; cursor: pointer; }
"""

FAILED = "The passkey did not sign in. Try again."

# The page asks the passkey on every visit, and sends the whole answer
# of navigator.credentials.get().
SCRIPT = """
const main = document.querySelector("main");
const failed = document.querySelector("#failed");
document.querySelector("button").addEventListener("click", async () => {
  failed.hidden = true;
  try {
    const options = await fetch("/api/auth/passkey/options", { method: "POST" });
    const publicKey = PublicKeyCredential.parseRequestOptionsFromJSON(await options.json());
    const credential = await navigator.credentials.get({ publicKey });
    const response = await fetch("/api/auth/authorize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ request: main.dataset.request, credential: credential.toJSON() }),
    });
    if (!response.ok) throw new Error(String(response.status));
    location.assign((await response.json()).redirect);
  } catch {
    failed.hidden = false;
  }
});
"""


def document(language: str, title: str, body: str) -> str:
    """Wrap a body in a page with its language and title."""
    return (
        f'<!doctype html><html lang="{escape(language)}"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(title)}</title><style>{STYLE}</style></head>"
        f"<body>{body}</body></html>"
    )


def authorize(translation: GNUTranslations, request: str) -> str:
    """Render the page that signs in with a passkey."""
    t = translation.gettext
    body = (
        f'<main data-request="{escape(request)}"><h1>{escape(t("Sign in"))}</h1>'
        f'<button type="button">{escape(t("Sign in with a passkey"))}</button>'
        f'<p id="failed" role="alert" hidden>{escape(t(FAILED))}</p>'
        f"</main><script>{SCRIPT}</script>"
    )
    return document(translation.info().get("language", ""), t("Sign in"), body)


def invalid(translation: GNUTranslations) -> str:
    """Render the page of a request without a registered client."""
    t = translation.gettext
    message = t("This sign-in request is not valid. Go back to the app and try again.")
    body = f"<main><h1>{escape(t('Sign in'))}</h1><p>{escape(message)}</p></main>"
    return document(translation.info().get("language", ""), t("Sign in"), body)

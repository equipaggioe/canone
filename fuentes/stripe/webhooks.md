# Recibe los eventos de Stripe en tu punto de conexión de webhook

Recibe eventos de Stripe en tu punto de conexión de webhook para que la integración pueda activar reacciones automáticamente.

Puedes crear un punto de conexión de webhook HTTPS para recibir eventos. Después de registrar un punto de conexión de webhook, Stripe le envía datos en tiempo real cuando se producen [eventos](https://docs.stripe.com/event-destinations.md#events-overview) en tu cuenta de Stripe. Stripe utiliza HTTPS para enviar eventos de webhook a tu aplicación como carga útil de JSON que incluye la información del evento.

Recibir eventos webhook te ayuda a responder a eventos asincrónicos, como cuando el banco de un cliente confirma un pago, un cliente disputa un cargo, o un pago recurrente se realiza correctamente.

También puedes consumir eventos de Stripe en tu infraestructura de AWS o Azure si los envías directamente a [Amazon EventBridge](https://docs.stripe.com/event-destinations/eventbridge.md) o [Azure Event Grid](https://docs.stripe.com/event-destinations/eventgrid.md).

Completa los siguientes pasos para empezar a recibir eventos de webhook en tu aplicación. Puedes registrar y crear un único punto de conexión que procese distintos tipos de eventos simultáneamente, o bien configurar puntos de conexión individuales para eventos específicos.

## Cómo configurar tu punto de conexión

Usa la pestaña [API](https://docs.stripe.com/api/v2/event-destinations.md) o [Webhooks](https://dashboard.stripe.com/webhooks) en Workbench para registrar la URL accesible de tu punto de conexión de webhook para que Stripe sepa a dónde enviar los eventos. Puedes registrar hasta 16&nbsp;puntos de conexión de webhook con Stripe. Los puntos de conexión de webhook registrados deben ser URL HTTPS de acceso público.

- Si tienes un servidor localhost, pero no tienes una URL HTTPS de acceso público, puedes usar una herramienta de creación de túneles como [ngrok](https://ngrok.com/) para generar una URL HTTPS temporal de acceso público y usarla con fines de prueba.
- Como alternativa, puedes [hacer pruebas de forma local mediante la CLI de Stripe](https://docs.stripe.com/webhooks.md#local-listener) antes de registrar una URL HTTPS de acceso público.

### Formato de URL del webhook

El formato de la URL para registrar un punto de conexión del webhook es el siguiente:

```
https://<your-website>/<your-webhook-endpoint>
```

Por ejemplo, si tu dominio es `https://mycompanysite.com` y la ruta a tu punto de conexión de webhook es `@app.route('/stripe_webhooks', methods=['POST'])`, especifica `https://mycompanysite.com/stripe_webhooks` como la URL del punto de conexión.

### Crea un destino de evento para el punto de conexión del webhook

#### Dashboard

Para crear un nuevo punto de conexión de webhook en el Dashboard, haz lo siguiente:

1. Abre la pestaña [Webhooks](https://dashboard.stripe.com/webhooks) de Workbench.
2. Haz clic en **Crear un destino de evento**.
3. Selecciona **Tu cuenta** para escuchar los eventos de tu propia cuenta.
4. Selecciona la versión de API del [objeto events](https://docs.stripe.com/api/events.md) que quieras consumir.
5. Selecciona los [tipos de eventos](https://docs.stripe.com/api/events/types.md) que quieras enviar a un punto de conexión de webhooks.
6. Selecciona **Continuar** y, luego, selecciona **Punto de conexión del webhook** como el tipo de destino.
7. Haz clic en **Continuar** y, luego, proporciona la **URL del punto de conexión** y una descripción opcional del webhook.
8. En la página de configuración del webhook aparece un secreto de firma que comienza con `whsec_`. Haz clic en **Revelar secreto** y copia el valor para usarlo cuando vayas a [crear un controlador](https://docs.stripe.com/webhooks.md#webhook-endpoint-def).

> [Workbench](https://docs.stripe.com/workbench.md) reemplaza el antiguo [Dashboard para desarrolladores](https://docs.stripe.com/development/dashboard.md). Todavía puedes [crear un punto de conexión de webhook nuevo](https://docs.stripe.com/development/dashboard/webhooks.md) en el Dashboard para desarrolladores, aunque te recomendamos usar Workbench.

#### API

Usa el punto de conexión [/v2/core/event_destinations](https://docs.stripe.com/api/v2/event-destinations.md) para registrar un punto de conexión nuevo.

#### Eventos instantáneos

Para escuchar [eventos snapshot](https://docs.stripe.com/api/events/types.md) desde tu propia cuenta, establece el valor [event_payload](https://docs.stripe.com/api/v2/core/event-destinations/create.md#v2_create_event_destinations-event_payload) en `snapshot` y el valor [enabled_events](https://docs.stripe.com/api/v2/core/event-destinations/create.md#v2_create_event_destinations-enabled_events) en los tipos de eventos que quieres enviar al punto de conexión de webhook:

```curl
curl -X POST https://api.stripe.com/v2/core/event_destinations \
  -H "Authorization: Bearer <<YOUR_SECRET_KEY>>" \
  -H "Stripe-Version: 2026-08-26.preview" \
  --json '{
    "name": "My event destination",
    "type": "webhook_endpoint",
    "events_from": [
        "@self"
    ],
    "event_payload": "snapshot",
    "enabled_events": [
        "payment_intent.succeeded",
        "payment_intent.payment_failed"
    ],
    "webhook_endpoint": {
        "url": "https://mycompanysite.com/webhook"
    },
    "include": [
        "webhook_endpoint.signing_secret"
    ]
  }'
```

La salida contiene un valor `webhook_endpoint.signing_secret` que comienza con `whsec_`. Copia este valor para usarlo cuando vayas a [crear un controlador](https://docs.stripe.com/webhooks.md#webhook-endpoint-def).

#### Eventos breves

Si usas [eventos breves](https://docs.stripe.com/api/v2/core/events/event-types.md), deberás registrar un punto de conexión de webhook distinto. Obtén más información sobre [las diferencias entre eventos breves y snapshot](https://docs.stripe.com/event-destinations.md#events-overview).

Para escuchar [eventos breves](https://docs.stripe.com/api/v2/core/events/event-types.md) desde tu propia cuenta, establece el valor [event_payload](https://docs.stripe.com/api/v2/core/event-destinations/create.md#v2_create_event_destinations-event_payload) en `thin` y el valor [enabled_events](https://docs.stripe.com/api/v2/core/event-destinations/create.md#v2_create_event_destinations-enabled_events) en los tipos de eventos que quieres enviar al punto de conexión de webhook:

```curl
curl -X POST https://api.stripe.com/v2/core/event_destinations \
  -H "Authorization: Bearer <<YOUR_SECRET_KEY>>" \
  -H "Stripe-Version: 2026-08-26.preview" \
  --json '{
    "name": "My event destination",
    "type": "webhook_endpoint",
    "events_from": [
        "@self"
    ],
    "event_payload": "thin",
    "enabled_events": [
        "v1.billing.meter.error_report_triggered"
    ],
    "webhook_endpoint": {
        "url": "https://mycompanysite.com/webhook"
    },
    "include": [
        "webhook_endpoint.signing_secret"
    ]
  }'
```

La salida contiene un valor `webhook_endpoint.signing_secret` que comienza con `whsec_`. Copia este valor para usarlo cuando vayas a [crear un controlador](https://docs.stripe.com/webhooks.md#webhook-endpoint-def).

### Hacer pruebas de forma local sin una URL registrada

Si no tienes registrada una URL de HTTPS de acceso público, puedes probar los webhook en el entorno local si usas la CLI de Stripe para [reenviar los eventos al punto de conexión local](https://docs.stripe.com/cli/use-cli#forward-events-to-your-local-webhook-endpoint):

1. Si aún no lo has hecho, [instala la CLI de Stripe](https://docs.stripe.com/cli/install) en tu equipo.

2. Inicia sesión en tu cuenta de Stripe y configura la CLI con la ejecución de`stripe login` en la línea de comandos.

3. Permite que tu servidor local reciba un evento simulado mediante la ejecución de [stripe listen](https://docs.stripe.com/cli/listen), lo que dependerá del alcance y el tipo de evento:

   #### Reenvía eventos con instantánea

   Usa el comando siguiente para reenviar [eventos snapshot](https://docs.stripe.com/event-destinations.md#events-overview) de tu cuenta a tu sistema de escucha local.

   ```bash
   stripe listen --forward-to localhost:4242/webhook
   ```

   #### Reenvía eventos breves

   Usa el comando siguiente para reenviar [eventos breves](https://docs.stripe.com/event-destinations.md#events-overview) de tu cuenta a tu sistema de escucha local.

   ```bash
   stripe listen --forward-thin-to localhost:4242/webhook --thin-events "*"
   ```

   Este comando presupone que el sitio web de tu servidor local usa el puerto 4242 con un punto de conexión `POST /webhook`, que puedes configurar cuando [crees un controlador](https://docs.stripe.com/webhooks.md#webhook-endpoint-def).

4. El comando `stripe listen` emite como salida el `{{WEBHOOK_SIGNING_SECRET}}`. Copia este valor para usarlo cuando vayas a [crear un controlador](https://docs.stripe.com/webhooks.md#webhook-endpoint-def).

   ```output
   Ready! Your webhook signing secret is '{{WEBHOOK_SIGNING_SECRET}}' (^C to quit)
   ```

> Para usar el argumento `--forward-to` con `stripe listen`, debes ejecutar el comando con la [CLI de Stripe](https://docs.stripe.com/cli.md) en una terminal. No se puede ejecutar este comando en [Workbench Shell](https://docs.stripe.com/workbench/shell.md) porque no admite el argumento `--forward-to`.

## Crea un controlador

Configura una función de punto de conexión HTTP o HTTPS que pueda aceptar solicitudes de webhooks con un método POST. Si todavía estás desarrollando tu función de punto de conexión en una máquina local, puedes usar HTTP. Una vez que sea de acceso público, la función de punto de conexión de tu webhook debe usar HTTPS.

Usa la referencia de la API Stripe para identificar los [objetos de evento breve](https://docs.stripe.com/api/v2/core/events/event-types.md) o los [objetos de evento instantáneos](https://docs.stripe.com/api/events/types.md) que tu servicio de webhook debe procesar.

Configura tu función de punto de conexión para que:

- Procesamiento de peticiones POST con una carga útil JSON que incluye la información del evento.
- Se verifica si Stripe generó la solicitud de webhook con la carga útil JSON, el encabezado `Stripe-Signature` y el secreto de firma de webhooks `whsec_` del paso anterior. Si falla la verificación, aparecerá un error.
- Devuelva de inmediato un código de estado correcto (`2xx`) antes de que alguna lógica compleja pueda provocar un error de tiempo de espera agotado. Por ejemplo, debes devolver una respuesta `200` antes de registrar la factura del cliente como pagada en tu sistema contable.

> #### No manipules el cuerpo de la solicitud sin procesar
> 
> Stripe requiere que el cuerpo sin formato de la solicitud realice la verificación de la firma. Si estás usando un framework, asegúrate de que no manipule el cuerpo sin formato. Cualquier manipulación al cuerpo sin formato de la solicitud hará que la verificación falle.
> 
> Descubre cómo [solucionar problemas de errores de verificación de firmas](https://docs.stripe.com/webhooks/signature.md).

#### Punto de conexión de ejemplo

Este fragmento de código es una función de webhook configurada para verificar los eventos recibidos de una cuenta de Stripe, controlar los eventos y devolver respuestas `200`. Refiérete al controlador de eventos [con instantánea](https://docs.stripe.com/event-destinations.md#events-overview) cuando uses recursos de la API v1 y refiérete al controlador de eventos [breves](https://docs.stripe.com/event-destinations.md#events-overview) cuando uses recursos de la API v2.

#### Controlador de eventos con instantánea

Al crear un controlador de eventos con instantánea, usa la definición del objeto API en el momento del evento para la lógica. Para ello, accede a los campos `data.object` del evento. También puedes recuperar el recurso API de la API de Stripe para acceder a la definición de objeto más reciente y actualizada.

#### Ruby

```ruby
require 'json'
require 'stripe'

client = Stripe::StripeClient.new(ENV.fetch('STRIPE_API_KEY'))

# Replace this endpoint secret with your unique endpoint secret key
# If you're testing with the CLI, run 'stripe listen' to find the secret key
# If you defined your endpoint using the API or the Dashboard, check your webhook settings for your endpoint secret: https://dashboard.stripe.com/webhooks
endpoint_secret = 'whsec_...';

# Using Sinatra
post '/webhook' do
  payload = request.body.read
  event = nil

  begin
    event = Stripe::Event.construct_from(
      JSON.parse(payload, symbolize_names: true)
    )
  rescue JSON::ParserError => e
    # Invalid payload
    status 400
    return
  end

  # Check that you have configured webhook signing
  if endpoint_secret
    # Retrieve the event by verifying the signature using the raw body and the endpoint secret
    signature = request.env['HTTP_STRIPE_SIGNATURE'];
    begin
      event = Stripe::Webhook.construct_event(
        payload, signature, endpoint_secret
      )
    rescue Stripe::SignatureVerificationError => e
      puts "⚠️  Webhook signature verification failed. #{e.message}"
      status 400
    end
  end

  # Handle the event
  case event.type
  when 'payment_intent.succeeded'
    payment_intent = event.data.object # contains a Stripe::PaymentIntent
    # Then define and call a method to handle the successful payment intent.
    # handle_payment_intent_succeeded(payment_intent)
  when 'payment_method.attached'
    payment_method = event.data.object # contains a Stripe::PaymentMethod
    # Then define and call a method to handle the successful attachment of a PaymentMethod.
    # handle_payment_method_attached(payment_method)
  # ... handle other event types
  else
    puts "Unhandled event type: #{event.type}"
  end

  status 200
end
```

#### Controlador de eventos ligeros (Clover+)

Cuando crees un controlador de eventos ligeros, utiliza el método `fetchRelatedObject()` para recuperar la última versión del objeto asociado al evento. Los eventos pueden contener [datos adicionales](https://docs.stripe.com/event-destinations.md#fetch-data) que solo puedes recuperar a través del método de instancia `.fetchEvent()` en `EventNotification`. La forma exacta de esos datos depende del `type` del Evento.

Los tipos de eventos deben estar disponibles en el momento del lanzamiento para generar clases en esa versión del SDK. Para gestionar eventos en los que el SDK no tiene clases, utiliza la clase `UnknownEventNotification`.

#### Python

```python
import os
from stripe import StripeClient
from stripe.events import UnknownEventNotification

from flask import Flask, request, jsonify

app = Flask(__name__)
api_key = os.environ.get("STRIPE_API_KEY", "")
webhook_secret = os.environ.get("WEBHOOK_SECRET", "")

client = StripeClient(api_key)

@app.route("/webhook", methods=["POST"])
def webhook():
    webhook_body = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event_notif = client.parse_event_notification(
            webhook_body, sig_header, webhook_secret
        )

        # type checkers will narrow the type based on the `type` property
        if event_notif.type == "v1.billing.meter.error_report_triggered":
            # in this block, event_notification is typed as
            # a V1BillingMeterErrorReportTriggeredEventNotification

            # there's basic info about the related object in the notification
            print(f"Meter w/ id {event_notif.related_object.id} had a problem")

            # or you can fetch the full object form the API for more details
            meter = event_notif.fetch_related_object()
            print(
                f"Meter {meter.display_name} ({meter.id}) had a problem"
            )

            # And you can always fetch the full event:
            event = event_notif.fetch_event()
            print(f"More info: {event.data.developer_message_summary}")

        elif event_notif.type == "v1.billing.meter.no_meter_found":
            # in this block, event_notification is typed as
            # a V1BillingMeterNoMeterFoundEventNotification

            # that class doesn't define `fetch_related_object` because the event
            # has no related object.
            # so this line would correctly give a type error:
            # meter = event_notif.fetch_related_object()

            # but fetching the event always works:
            event = event_notif.fetch_event()
            print(
                f"Err! No meter found: {event.data.developer_message_summary}"
            )

        # Events that were introduced after this SDK version release are
        # represented as `UnknownEventNotification`s.
        # They're valid, the SDK just doesn't have corresponding classes for them.
        # You must match on the "type" property instead.
        elif isinstance(event_notif, UnknownEventNotification):
            # these lines are optional, but will give you more accurate typing in this block
            from typing import cast

            event_notif = cast(UnknownEventNotification, event_notif)

            # continue matching on the type property
            # from this point on, the `related_object` property _may_ be None
            # (depending on the event type)
            if event_notif.type == "some.new.event":
                # if this event type has a related object, you can fetch it
                obj = event_notif.fetch_related_object()
                # otherwise, `obj` will just be `None`
                print(f"Related object: {obj}")

                # you can still fetch the full event, but it will be untyped
                event = event_notif.fetch_event()
                print(f"New event: {event.data}")  # type: ignore

        return jsonify(success=True), 200
    except Exception as e:
        return jsonify(error=str(e)), 400
```

## Prueba tu controlador

Antes de pasar a modo activo con tu función del punto de conexión de webhook, te recomendamos probar la integración de tu aplicación desencadenando eventos en un entorno de prueba o enviando eventos de prueba con la [CLI de Stripe](https://docs.stripe.com/cli.md).

### Cómo activar eventos de prueba

Para enviar eventos de prueba, activa un tipo de evento al que esté suscrito el destino de tu evento. Para ello, crea manualmente un objeto en el Dashboard de Stripe. Cómo activar eventos con [Stripe para VS Code](https://docs.stripe.com/stripe-vscode.md).

#### Activar un evento de instantánea

Puedes usar el siguiente comando en [Stripe Shell](https://docs.stripe.com/workbench/shell.md) o [Stripe CLI](https://docs.stripe.com/cli.md). Este ejemplo activa un evento `payment_intent.succeeded`:

```bash
stripe trigger payment_intent.succeeded
Running fixture for: payment_intent
Trigger succeeded! Check dashboard for event details.
```

#### Activar un evento breve

Puedes usar el siguiente comando en la [CLI de Stripe](https://docs.stripe.com/cli.md). Este ejemplo activa un evento `v1.billing.meter.error_report_triggered`:

```bash
stripe trigger v1.billing.meter.error_report_triggered
Setting up fixture for: list_billing_meters
Running fixture for: list_billing_meters
Setting up fixture for: billing_meter
Running fixture for: billing_meter
Setting up fixture for: list_billing_meters_after_creation
Running fixture for: list_billing_meters_after_creation
Setting up fixture for: billing_meter_event_session
Running fixture for: billing_meter_event_session
Setting up fixture for: create_billing_meter_event_stream
Running fixture for: create_billing_meter_event_stream
Trigger succeeded! Check dashboard for event details.
```

## Optional: Cómo crear un destino de evento para Connect

Cuando [creas un destino de evento](https://docs.stripe.com/webhooks.md#create-webhook-endpoint) como una plataforma de Connect, eliges qué ámbito escuchará:

#### Dashboard

- **Tu cuenta**: eventos de recursos en tu cuenta.
- **Cuentas conectadas**: eventos de recursos que pertenecen a tus cuentas conectadas.

#### API

- [events_from=[“@self”]](https://docs.stripe.com/api/v2/core/event-destinations/create.md#v2_create_event_destinations-events_from): eventos de recursos en tu cuenta.
- [events_from=[“@accounts”]](https://docs.stripe.com/api/v2/core/event-destinations/create.md#v2_create_event_destinations-events_from): eventos de recursos que pertenecen a tus cuentas conectadas.

Registra un destino de evento para **Cuentas conectadas** para recibir eventos para los recursos que pertenecen a tus cuentas conectadas. Los ejemplos incluyen [cargos Direct](https://docs.stripe.com/connect/direct-charges.md), clientes y métodos de pago de cuentas conectadas, transferencias fallidas y actualizaciones de ciclo de vida de la cuenta conectada heredada snapshot, como el onboarding, la verificación, cambios de cuenta externa y desconexiones de cuenta. Para la versión&nbsp;2 de Account, este ámbito solo recibe eventos snapshot de los objetos Account que representan tus cuentas conectadas.

Según tu integración de Connect, quizá también debas registrar un destino de evento para **Tu cuenta**. Algunos de los motivos son los siguientes:

- El procesamiento de eventos para recursos de tu cuenta de plataforma, que incluye clientes de la plataforma, cargos propiedad de la plataforma, [cargos a un destino](https://docs.stripe.com/connect/destination-charges.md) y [cargos y envíos de fondos separados](https://docs.stripe.com/connect/separate-charges-and-transfers.md).
- El procesamiento de eventos reducidos relacionados con objetos de la versión&nbsp;2 de Account que representan tus cuentas conectadas.

Consulta [Webhooks de Connect](https://docs.stripe.com/connect/webhooks.md?accounts-namespace=v2) para obtener más información.

### Prueba Connect en un entorno local sin una URL registrada

#### Eventos instantáneos

Usa el comando siguiente para reenviar [eventos snapshot](https://docs.stripe.com/event-destinations.md#events-overview) de tus cuentas conectadas a tu sistema de escucha local.

```bash
stripe listen --forward-connect-to localhost:4242/webhook
```

#### Eventos breves

Usa el comando siguiente para reenviar [eventos breves](https://docs.stripe.com/event-destinations.md#events-overview) de tus cuentas conectadas a tu sistema de escucha local.

```bash
stripe listen --forward-thin-connect-to localhost:4242/webhook --thin-events "*"
```

## Optional: Cómo crear un destino de eventos para Organizations

Cuando [creas un destino de eventos](https://docs.stripe.com/webhooks.md#create-webhook-endpoint) como una Organization, eliges el alcance que escucha:

#### Dashboard

- **Cuentas en tu organización**: eventos de los recursos de las cuentas de tu organización.
- **Cuentas conectadas**: eventos de los recursos dentro de las cuentas conectadas de tu organización.

#### API

- [events_from=[“@organization_members”]](https://docs.stripe.com/api/v2/core/event-destinations/create.md#v2_create_event_destinations-events_from): eventos de los recursos de las cuentas de tu organización.
- [events_from=[“@organization_members/@accounts”]](https://docs.stripe.com/api/v2/core/event-destinations/create.md#v2_create_event_destinations-events_from): eventos de los recursos dentro de las cuentas conectadas de tu organización.

### Comportamientos de tipo de evento no admitidos para destinos de eventos de una organización

Stripe envía la mayoría de los tipos de eventos de forma asincrónica, pero espera una respuesta para algunos de ellos. En estos casos, Stripe se comporta de forma diferente dependiendo de si el destino del evento responde o no.

Si el destino de tu evento recibe eventos de la [Organización](https://docs.stripe.com/get-started/account/orgs.md), aquellos que requieren una respuesta tienen las siguientes limitaciones:

- No puedes suscribirte a `issuing_authorization.request` para los destinos de la organización. En su lugar, configura un [punto de conexión de webhook](https://docs.stripe.com/webhooks.md#example-endpoint) en una cuenta de Stripe dentro de la organización para suscribirte a este tipo de evento. Usa `issuing_authorization.request` para autorizar solicitudes de compra en tiempo real.
- Los destinos de la organización que reciben `checkout_sessions.completed` no pueden [gestionar el comportamiento](https://docs.stripe.com/checkout/fulfillment.md#redirect-hosted-checkout) de redireccionamiento cuando insertas [Procesos de compra](https://docs.stripe.com/payments/checkout.md) directamente en tu sitio web o rediriges a los clientes a una página de pago alojada en Stripe. Para influir en el comportamiento de redireccionamiento de procesos de compra, procesa este tipo de eventos con un [punto de conexión](https://docs.stripe.com/webhooks.md#example-endpoint) webhook configurado en una cuenta de Stripe dentro de la organización.
- Los destinos de la organización que responden sin éxito a un evento `invoice.created` no pueden influir en la [finalización automática de facturas cuando se usa cobro automático](https://docs.stripe.com/billing/subscriptions/webhooks.md#understand). Debes procesar este tipo de evento con un [punto de conexión webhook](https://docs.stripe.com/webhooks.md#example-endpoint) configurado en una cuenta de Stripe dentro de la organización para activar la finalización automática de facturas.

#### Uso de `context`

#### Eventos instantáneos

Este fragmento de código es una función de webhooks configurada para verificar los eventos recibidos, detectar la cuenta de origen, si corresponde, gestionar el evento y devolver una respuesta `200`.

#### Ruby

```ruby
require 'json'

client = Stripe::StripeClient.new('sk_...')

# Using Sinatra
post '/webhook' do
  payload = request.body.read
  event = nil

  begin
    event = Stripe::Event.construct_from(
      JSON.parse(payload, symbolize_names: true)
    )
  rescue JSON::ParserError => e
    # Invalid payload
    status 400
    return
  end

  # Extract the context
  context = event.context

  # Define your API key variables (ideally loaded securely)
  ACCOUNT_123_API_KEY = "sk_test_123"
  ACCOUNT_456_API_KEY = "sk_test_456"

  account_api_keys = {
    "account_123" => ACCOUNT_123_API_KEY,
    "account_456" => ACCOUNT_456_API_KEY
  }

  api_key = account_api_keys[context]

  if api_key.nil?
    puts "No API key found for context: #{context}"
    status 400
    return
  end

  # Handle the event
  case event.type
  when 'customer.created'
    customer = event.data.object

    begin

      latest_customer = client.v1.customers.retrieve(customer.id, {api_key: api_key})
      handle_customer_created(latest_customer, context)
    rescue => e
      puts "Error retrieving customer: #{e.message}"
      status 500
      return
    end

  when 'payment_method.attached'
    payment_method = event.data.object

    begin
      latest_payment_method = client.v1.payment_methods.retrieve(payment_method.id, {api_key: api_key})
      handle_payment_method_attached(latest_payment_method, context)
    rescue => e
      puts "Error retrieving payment method: #{e.message}"
      status 500
      return
    end

  else
    puts "Unhandled event type: #{event.type}"
  end

  status 200
end
```

#### Controlador de eventos ligeros (Clover+)

Utiliza la propiedad `context` de `EventNotification` para identificar la cuenta de eventos dentro de tu [organización](https://docs.stripe.com/get-started/account/orgs.md). Debes definir el [encabezado de Stripe Context](https://docs.stripe.com/context.md) de forma manual para todas las llamadas API, excepto `.fetchRelatedObject()` y `.fetchEvent()`, que lo hacen por ti de forma automática.

#### Python

```python
org_api_key = os.environ.get("STRIPE_API_KEY")
webhook_secret = os.environ.get("WEBHOOK_SECRET")
client = StripeClient(org_api_key)

# inside your webhook handler
event_notification = client.parse_event_notification(payload, sig_header, webhook_secret)

# uses `context` automatically
event_notification.fetch_event()

# pass context manually for other API requests
client.v1.invoices.list(stripe_context=event_notification.context)
```

## Depura las integraciones de webhooks

Pueden ocurrir varios tipos de problemas al entregar eventos al punto de conexión de tu webhook:

- Es posible que Stripe no pueda enviar un evento al punto de conexión de tu webhook.
- El punto de conexión de tu webhook podría tener un problema de SSL.
- Tu conectividad de red es intermitente.
- El punto de conexión de tu webhook no está recibiendo los eventos que esperas recibir.

### Ver las entregas de eventos

Para ver las entregas de eventos, abre [Workbench](https://docs.stripe.com/workbench.md), selecciona el punto de conexión del webhook en **Webhooks** y, a continuación, selecciona la pestaña **Eventos**. La pestaña **Eventos** contiene una lista de eventos y muestra si tienen el estado `Entregado`, `Pendiente` o `Error`. Haz clic en un evento para ver los metadatos, que incluyen el código de estado HTTP de los intentos de entrega anteriores y la hora de las entregas futuras pendientes.

También puedes usar la [CLI de Stripe](https://docs.stripe.com/cli.md) para [escuchar eventos](https://docs.stripe.com/webhooks.md#test-webhook) directamente en tu terminal.

### Corrige los códigos de estado HTTP

Cuando un evento muestra un código de estado `200`, indica una entrega correcta al punto de conexión de webhook. También puedes recibir un código de estado que no sea `200`. En la siguiente tabla, encontrarás una lista de códigos de estado HTTP comunes y soluciones recomendadas.

| Estado de webhook pendiente | Descripción | Corregir |
| --- | --- | --- |
| (Error al establecer conexión) ERR | No podemos establecer conexión con el servidor de destino. | Asegúrate de que tu dominio de host sea de acceso público en Internet. |
| (`302`) ERR (u otro estado `3xx`) | El servidor de destino intentó redirigir la solicitud a otra ubicación. Consideramos las respuestas de redireccionamiento a las solicitudes de webhook como errores. | Establece el destino del punto de conexión del webhook en la URL resuelta por el redireccionamiento. |
| (`400`) ERR (u otro estado `4xx`) | El servidor de destino no puede procesar la solicitud o no lo hará. Esta circunstancia puede darse cuando el servidor detecta un error (`400`), cuando la URL de destino tiene restricciones de acceso (`401`, `403`, `405`) o cuando la URL de destino no existe (`404`). | Asegúrate de que tu punto de conexión sea accesible públicamente en Internet y acepte el método HTTP POST. |
| (`500`) ERR (u otro estado `5xx`) | El servidor de destino encontró un error mientras se procesaba la solicitud. | Revisa los registros de tu aplicación para comprender por qué devuelve un error `500`. |
| (Error TLS) ERR | No pudimos establecer una conexión segura con el servidor de destino. Estos errores suelen deberse a los problemas con el certificado SSL/TLS o un certificado intermedio en la cadena de certificados del servidor de destino. Stripe requiere una versión `v1.2` de *TLS* (TLS refers to the process of securely transmitting data between the client—the app or browser that your customer is using—and your server. This was originally performed using the SSL (Secure Sockets Layer) protocol) o superior. | Realiza una [prueba de servidor SSL](https://www.ssllabs.com/ssltest/) para encontrar problemas que puedan causar este error. |
| (Se agotó el tiempo de espera) ERR | El servidor de destino tardó demasiado en responder a la solicitud de webhook. | Asegúrate de aplazar la lógica compleja y devuelve una respuesta correcta de inmediato en tu código de manejo de webhooks. |

## Comportamientos de entrega de eventos

Esta sección te ayuda a comprender los diferentes comportamientos que puedes esperar en cuanto a la forma en que Stripe envía eventos a tu punto de conexión de webhook.

### Reintentos automáticos

Stripe intenta entregar eventos en tu destino durante un máximo de tres&nbsp;días con un retroceso exponencial en modo activo. Consulta cuándo se hará el siguiente reintento, si corresponde, en la pestaña **Entregas de eventos** de tu destino de eventos. Reintentamos las entregas de eventos creadas en un entorno de prueba tres veces en el transcurso de unas pocas horas. Si tu destino se deshabilitó o se eliminó cuando realizamos un reintento, no permitiremos próximos reintentos. Sin embargo, si deshabilitas y, luego, vuelves a habilitar el destino del evento antes de que podamos reintentarlo, aún verás reintentos futuros.

### Reintentos manuales

Hay dos maneras de reintentar eventos manualmente:

- En el Dashboard de Stripe, haz click en **Reenviar** cuando estés viendo un evento específico. Esto funciona hasta 15 días después de la creación del evento.
- Con la [CLI de Stripe](https://docs.stripe.com/cli/events/resend), ejecuta el comando `stripe events resend <event_id> --webhook-endpoint=<endpoint_id>`. Esto funciona hasta 30 días después de la creación del evento.

Reenviar manualmente un evento que tuvo fallos de entrega previos a un punto de conexión webhook no descarta el [comportamiento automático de reintentos](https://docs.stripe.com/webhooks.md#automatic-retries) de Stripe, aunque este de como resultado un código de estado `2xx`. Aprende cómo[procesar eventos de webhook no entregados](https://docs.stripe.com/webhooks/process-undelivered-events.md) a fin de detener futuros intentos.

### Pedido de eventos

Stripe no garantiza la entrega de eventos en el orden en que se generaron. Por ejemplo, crear una suscripción puede generar los siguientes eventos:

- `customer.subscription.created`
- `invoice.created`
- `invoice.paid`
- `charge.created` (si hay un cargo)

Asegúrate de que el destino de tus eventos no dependa de recibirlos en un orden específico. Los eventos con instantánea registran `created` en segundos, por lo que distintos eventos pueden compartir una marca de tiempo. No uses `created` para determinar el orden de los eventos ni si ya procesaste un evento. En su lugar, haz un seguimiento de los [ID de eventos](https://docs.stripe.com/api/events/object.md#event_object-id) con el objetivo de identificar entregas duplicadas. También puedes usar la API a fin de recuperar cualquier objeto faltante. Por ejemplo, puedes recuperar los objetos factura, cargo y suscripción con la información de `invoice.paid` si recibes este evento primero.

### Control de versiones de la API

La versión de la API en la configuración de tu cuenta cuando ocurre el evento dicta la versión de la API y, por lo tanto, la estructura de un [Event](https://docs.stripe.com/api/events.md) enviado a tu destino. Por ejemplo, si tu cuenta está configurada en una versión anterior de la API, como 2015-02-16, y cambias la versión de la API para una solicitud específica con [control de versiones](https://docs.stripe.com/api.md#versioning), el objeto [Event](https://docs.stripe.com/api/events.md) generado y enviado a tu destino se seguirá basando en la versión de la API 2015-02-16. No puedes cambiar los objetos [Event](https://docs.stripe.com/api/events.md) después de la creación. Por ejemplo, si actualizas un cargo, el evento original del cargo no variará. Por lo tanto, las actualizaciones posteriores de la versión de la API de tu cuenta no alteran los objetos [Event](https://docs.stripe.com/api/events.md) existentes de forma retroactiva. La recuperación de un [Event](https://docs.stripe.com/api/events.md) anterior llamando a `/v1/events` con una versión más nueva de la API tampoco influye en la estructura del evento recibido. Puedes definir destinos de eventos de prueba para tu versión de API predeterminada o para la última versión de API. El [Event](https://docs.stripe.com/api/events.md) enviado al destino se estructura para la versión especificada del destino del evento.

## Prácticas recomendadas para usar webhooks

Revisa estas prácticas recomendadas para asegurarte de que tus puntos de conexión de webhook sigan siendo seguros y funcionen bien con tu integración.

### Maneja los eventos duplicados

Los puntos de conexión de webhooks ocasionalmente pueden recibir el mismo evento más de una vez. Para protegerte contra los recibos de eventos duplicados, puedes registrar los [ID de evento](https://docs.stripe.com/api/events/object.md#event_object-id) que procesaste y luego no procesar los eventos ya registrados.

En algunos casos, se generan y envían dos objetos Event separados. Para identificar estos duplicados, utiliza la ID del objeto en `data.object` junto con el `event.type`.

### Escucha únicamente los tipos de eventos que tu integración requiere

Configura tus puntos de conexión de webhook para recibir solo los tipos de evento que necesita tu integración. Si escuchas otros eventos (o todos los eventos), se producirá una saturación indebida en tu servidor que no recomendamos.

Puedes [modificar los eventos](https://docs.stripe.com/api/webhook_endpoints/update.md#update_webhook_endpoint-enabled_events) que recibe un punto de conexión de webhook en el Dashboard o con la API.

### Administra eventos de forma asíncrona

Configura el controlador para procesar los eventos entrantes con una cola asincrónica. Es posible que tengas problemas de escalabilidad si decides procesar los eventos de forma sincrónica. Cualquier aumento importante en las entregas de webhooks (por ejemplo, durante el comienzo del mes, cuando se renuevan todas las suscripciones) podría sobrecargar a los hosts de los puntos de conexión.

Las colas asincrónicas te permiten procesar los eventos simultáneos a una velocidad que el sistema puede admitir.

### Ruta de webhook exenta de la protección CSRF

Si usas Rails, Django u otro framework web, tu sitio podría comprobar automáticamente si cada solicitud POST contiene un *token CSRF*. Esta es una funcionalidad de seguridad importante que ayuda a protegerte a ti y a tus usuarios contra intentos de [falsificación de solicitudes en sitios cruzados](https://www.owasp.org/index.php/Cross-Site_Request_Forgery_\(CSRF\)). No obstante, esta medida de seguridad también puede impedir que tu sitio procese eventos legítimos. De ser así, quizá sea necesario que la ruta de webhooks quede exenta de la protección CSRF.

#### Rails

```ruby
class StripeController < ApplicationController
  # If your controller accepts requests other than Stripe webhooks,
  # you'll probably want to use `protect_from_forgery` to add CSRF
  # protection for your application. But don't forget to exempt
  # your webhook route!
  protect_from_forgery except: :webhook

  def webhook
    # Process webhook data in `params`
  end
end
```

### Recibe eventos con un servidor HTTPS

Si usas una URL HTTPS para tu punto de conexión de webhooks (obligatorio en modo activo), Stripe validará que la conexión con tu servidor sea segura antes de enviar tus datos de webhook. Para que esto funcione, tu servidor debe estar configurado correctamente de manera de admitir HTTPS con un certificado de servidor válido. Los webhooks de Stripe solo admiten versiones v1.2 y v1.3 de *TLS* (TLS refers to the process of securely transmitting data between the client—the app or browser that your customer is using—and your server. This was originally performed using the SSL (Secure Sockets Layer) protocol).

### Cambia los secretos de firma del punto de conexión periódicamente

El secreto que se usa para verificar que los eventos proceden de Stripe se puede modificar en la pestaña [Webhooks](https://dashboard.stripe.com/webhooks) en Workbench. Para mantener su seguridad, te recomendamos cambiar (rotar) los secretos de forma periódica o si sospechas que alguno está en riesgo.

Para cambiar un secreto:

1. En Workbench, haz clic en cada punto de conexión en la pestaña [Webhooks](https://dashboard.stripe.com/webhooks) para el que quieras cambiar el secreto.
2. Ve al menú de contenido adicional (⋯) y haz clic en **Cambiar secreto**. Puedes elegir que el secreto actual venza de inmediato o postergar su vencimiento hasta 24&nbsp;horas para tener tiempo de actualizar el código de verificación en tu servidor. Durante este lapso, habrá varios secretos activos para el punto de conexión. Stripe genera una firma por secreto hasta su vencimiento.

### Verifica que los eventos provengan de Stripe

Sin verificación, un atacante podría enviar eventos de webhook falsos a tu punto de conexión para desencadenar acciones como completar pedidos, conceder acceso a cuentas o modificar registros. Verifica siempre que los eventos de webhook proceden de Stripe antes de realizar cualquier acción.

Usa estas dos protecciones:

- **Lista de IP permitidas**: Stripe envía eventos de webhook desde una lista definida de [direcciones IP](https://docs.stripe.com/ips.md). Configura tu servidor o firewall para que solo acepte solicitudes de webhook procedentes de estas direcciones.
- **Verificación de firma**: Stripe firma cada evento de webhook con la inclusión de una firma en el encabezado `Stripe-Signature`. Verifica esta firma usando nuestras [bibliotecas oficiales](https://docs.stripe.com/webhooks.md#verify-signature) o sigue los [pasos de verificación manual](https://docs.stripe.com/webhooks.md?verify=verify-manually#verify-signature) para confirmar que el evento no fue enviado ni modificado por un tercero.

En la siguiente sección se describe cómo verificar las firmas de webhooks:

1. Recupera el secreto de tu punto de conexión.
2. Verifica la firma.

#### Cómo recuperar el secreto de tu punto de conexión

Usa Workbench y ve a la pestaña [Webhooks](https://dashboard.stripe.com/webhooks) para ver todos tus puntos de conexión. Selecciona el punto de conexión cuyo secreto deseas obtener y haz clic en **Haz clic para revelar**.

Stripe genera un secreto único para cada punto de conexión. Si usas el mismo punto de conexión para las [claves de API de prueba y activas](https://docs.stripe.com/keys.md#test-live-modes), el secreto será diferente para cada una. Además, si usas varios puntos de conexión, deberás obtener un secreto para cada uno en el que quieras verificar las firmas. Después de esta configuración, Stripe comenzará a firmar cada webhook que envía al punto de conexión.

#### Verifica la firma.

#### Haz la verificación con las bibliotecas oficiales (recomendada)

### Haz la verificación manual de las firmas de webhook con las bibliotecas oficiales

Recomendamos utilizar nuestras bibliotecas oficiales para verificar las firmas. Para realizar la verificación, proporciona la carga del evento, el encabezado `Stripe-Signature` y el secreto del punto de conexión. Si la verificación falla, verás un error.

Si recibes un error de verificación de firma, lee nuestra guía sobre [solución de problemas](https://docs.stripe.com/webhooks/signature.md).

> Stripe requiere que el cuerpo sin formato de la solicitud realice la verificación de la firma. Si estás usando un framework, asegúrate de que no manipule el cuerpo sin formato. Cualquier manipulación al cuerpo sin formato de la solicitud hará que la verificación falle.

#### Ruby

```ruby

# Don't put any keys in code. See https://docs.stripe.com/keys-best-practices.
# Find your keys at https://dashboard.stripe.com/apikeys.
client = Stripe::StripeClient.new('<<YOUR_SECRET_KEY>>')

require 'stripe'
require 'sinatra'

# If you are testing your webhook locally with the Stripe CLI you
# can find the endpoint's secret by running `stripe listen`
# Otherwise, find your endpoint's secret in your webhook settings in
# the Developer Dashboard
endpoint_secret = 'whsec_...'

# Using the Sinatra framework
set :port, 4242

post '/my/webhook/url' do
  payload = request.body.read
  sig_header = request.env['HTTP_STRIPE_SIGNATURE']
  event = nil

  begin
    event = Stripe::Webhook.construct_event(
      payload, sig_header, endpoint_secret
    )
  rescue JSON::ParserError => e
    # Invalid payload
    puts "Error parsing payload: #{e.message}"
    status 400
    return
  rescue Stripe::SignatureVerificationError => e
    # Invalid signature
    puts "Error verifying webhook signature: #{e.message}"
    status 400
    return
  end

  # Handle the event
  case event.type
  when 'payment_intent.succeeded'
    payment_intent = event.data.object # contains a Stripe::PaymentIntent
    puts 'PaymentIntent was successful!'
  when 'payment_method.attached'
    payment_method = event.data.object # contains a Stripe::PaymentMethod
    puts 'PaymentMethod was attached to a Customer!'
  # ... handle other event types
  else
    puts "Unhandled event type: #{event.type}"
  end

  status 200
end
```

#### Haz la verificación en forma manual

### Haz la verificación manual de las firmas de webhook

Si bien te recomendamos que uses nuestra biblioteca oficial para verificar firmas de eventos de webhook, puedes crear una solución personalizada siguiendo las indicaciones de esta sección.

El encabezado `Stripe-Signature` incluido en cada evento firmado contiene una marca de tiempo y una o más firmas que debes verificar. La marca de tiempo tiene el prefijo `t=`, y cada firma tiene un *esquema* como prefijo. Los esquemas comienzan con `v`, seguido de un número entero. Actualmente, el único esquema de firma en modo activo válido es `v1`. Para ayudar con las pruebas, Stripe envía una firma adicional con un esquema `v0` falso, para eventos en modo de prueba.

```
Stripe-Signature:
t=1492774577,
v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd,
v0=6ffbb59b2300aae63f272406069a9788598b792a944a07aba816edb039989a39
```

> Propocionamos nuevas líneas para obtener mayor claridad, pero un encabezado `Stripe-Signature` real va en una sola línea.

Stripe genera firmas usando un código de autenticación de mensajes basado en hash ([HMAC](https://en.wikipedia.org/wiki/Hash-based_message_authentication_code)) con [SHA-256](https://en.wikipedia.org/wiki/SHA-2). Para evitar los [ataques de degradación](https://en.wikipedia.org/wiki/Downgrade_attack), ignora todos los esquemas que no sean `v1`.

Puedes tener más de una firma con el mismo par esquema-secreto cuando [cambias el secreto de un punto de conexión](https://docs.stripe.com/webhooks.md#roll-endpoint-secrets) y mantienes activo el secreto anterior por un plazo máximo de 24&nbsp;horas. Durante este plazo, tu punto de conexión tendrá varios secretos activos, y Stripe generará una firma para cada uno de ellos.

Si deseas crear una solución manual para verificar firmas, debes completar los siguientes pasos:

#### Paso 1: extrae la marca de tiempo y las firmas del encabezado

Divide el encabezado con el carácter `,` como separador para obtener una lista de elementos. Luego, divide cada elemento con el carácter `=` como separador para obtener un par de prefijo y valor.

El valor del prefijo `t` corresponde a la marca de tiempo, mientras que `v1` corresponde a la firma (o firmas). Puedes descartar el resto de los elementos.

#### Paso 2: Prepara la cadena `signed_payload`

La cadena `signed_payload` se crea concatenando:

- La marca de tiempo (como cadena)
- El carácter `.`
- La carga JSON real (es decir, el cuerpo de la solicitud)

#### Paso 3: determina la firma prevista

Calcula un HMAC con la función hash SHA256. Usa el secreto de la firma del punto de conexión como la clave, y la cadena `signed_payload` como el mensaje.

#### Paso 4: Compara las firmas

Compara la firma (o firmas) en el encabezado con la firma prevista. Para una correspondencia de igualdad, calcula la diferencia entre la marca de tiempo actual y la recibida, y luego decide si la diferencia está dentro de tu tolerancia.

Para protegerte contra ataques de sincronización, usa una comparación de cadenas de tiempo constante para comparar la firma esperada con cada una de las firmas recibidas.

### Cómo prevenir ataques de reproducción

Un [ataque de reproducción](https://en.wikipedia.org/wiki/Replay_attack) se produce cuando un atacante intercepta una carga válida y su firma, y luego la vuelve a transmitir. Para mitigar estos ataques, Stripe incluye una marca de tiempo en el encabezado `Stripe-Signature`. Dado que esta marca de tiempo forma parte de la carga firmada, también se verifica mediante la firma, por lo que un atacante no puede cambiar la marca de tiempo sin invalidar la firma. Si la firma es válida, pero la marca de tiempo es demasiado antigua, puedes hacer que tu aplicación rechace la carga.

De manera predeterminada, nuestras bibliotecas tienen una tolerancia de 5 minutos entre la marca de tiempo y la hora actual. Proporciona un parámetro adicional al verificar las firmas para modificar esta tolerancia. Usa el protocolo de tiempo de redes ([NTP](https://en.wikipedia.org/wiki/Network_Time_Protocol)) para garantizar que el clock de tu servidor sea preciso y esté sincronizado con la hora de los servidores de Stripe.

> No uses un valor de tolerancia `0`. El uso de un valor de tolerancia `0` deshabilita por completo la comprobación reciente.

Stripe genera la marca de tiempo y la firma cada vez que enviamos un evento a tu punto de conexión. Si Stripe reintenta un evento (por ejemplo, porque el punto de conexión envió un código de estado que no es `2xx`), se generan una firma y una marca de tiempo nuevas para el nuevo intento de entrega.

### Devuelve rápidamente una respuesta 2xx

Tu [punto de conexión](https://docs.stripe.com/webhooks.md#example-endpoint) debe devolver rápidamente un código de estado correcto (`2xx`) antes de cualquier lógica compleja que pueda causar un tiempo de espera excedido. Por ejemplo, debes devolver una respuesta `200` antes de actualizar la factura de un cliente como pagada en tu sistema de contabilidad.

## See also

- [Envia eventos a Amazon EventBridge](https://docs.stripe.com/event-destinations/eventbridge.md)
- [Enviar eventos a Azure Event Grid](https://docs.stripe.com/event-destinations/eventgrid.md)
- [Lista de tipos de eventos ligeros](https://docs.stripe.com/api/v2/core/events/event-types.md)
- [Lista de tipos de eventos con instantánea](https://docs.stripe.com/api/events/.md)
- [Generador interactivo de puntos de conexión de webhooks](https://docs.stripe.com/webhooks/quickstart.md)

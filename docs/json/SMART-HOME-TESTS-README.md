# Alexa Smart Home Directive Tests

These tests simulate Alexa Smart Home API directives for device control.

## Discovery Test

**alexa-discovery-test.json**
```json
{
  "directive": {
    "header": {
      "namespace": "Alexa.Discovery",
      "name": "Discover"
    }
  }
}
```
- Discovers all Home Assistant devices
- Returns endpoint list with capabilities
- Use this first to verify HA connection

## Power Control Tests

**alexa-power-on-test.json**
- Turns on a device (light.living_room)
- Tests PowerController.TurnOn
- **IMPORTANT:** Change `endpointId` to match your HA entity

**alexa-power-off-test.json**
- Turns off a device (switch.bedroom_fan)
- Tests PowerController.TurnOff
- **IMPORTANT:** Change `endpointId` to match your HA entity

## Brightness Control Test

**alexa-brightness-test.json**
- Sets brightness to 75% (light.kitchen)
- Tests BrightnessController.SetBrightness
- **IMPORTANT:** Change `endpointId` to your dimmable light entity

## Thermostat Control Test

**alexa-thermostat-test.json**
- Sets temperature to 72°F (climate.living_room)
- Tests ThermostatController.SetTargetTemperature
- **IMPORTANT:** Change `endpointId` to your thermostat entity

## How to Customize These Tests

### Step 1: Get Your Entity IDs

Run the discovery test first, then check the response for your actual entity IDs:

```json
{
  "event": {
    "payload": {
      "endpoints": [
        {
          "endpointId": "light.your_actual_light_name"
        }
      ]
    }
  }
}
```

### Step 2: Update Test Files

Replace the `endpointId` values in the test JSON files:

**Before:**
```json
"endpointId": "light.living_room"
```

**After:**
```json
"endpointId": "light.your_actual_light_name"
```

### Step 3: Test Device Control

1. Run discovery test to verify devices are exposed
2. Copy entity ID from discovery response
3. Update power control test with your entity ID
4. Run power control test
5. Verify device changed state in Home Assistant

## Understanding Smart Home Responses

### Successful Control Response
```json
{
  "event": {
    "header": {
      "namespace": "Alexa",
      "name": "Response"
    },
    "payload": {}
  },
  "context": {
    "properties": [...]
  }
}
```

### Error Response
```json
{
  "event": {
    "header": {
      "namespace": "Alexa",
      "name": "ErrorResponse"
    },
    "payload": {
      "type": "ENDPOINT_UNREACHABLE",
      "message": "..."
    }
  }
}
```

## Common Smart Home Errors

**ENDPOINT_UNREACHABLE**
- Device not found in Home Assistant
- Entity ID incorrect or not exposed
- Home Assistant not responding

**INVALID_DIRECTIVE**
- Directive not supported
- Device doesn't support the capability
- Malformed request

**INTERNAL_ERROR**
- Home Assistant connection failed
- Invalid access token
- Network timeout

## Testing Workflow

1. **Discovery** - Verify devices are found
2. **Power Control** - Test basic on/off
3. **Advanced Controls** - Test brightness, temperature, etc.
4. **Error Cases** - Test with invalid entity IDs
5. **Live Testing** - Enable skill and test with voice

## Pro Tips

- Always run discovery first to get current entity IDs
- Test with one device type at a time
- Check Home Assistant state after each test
- Monitor CloudWatch logs for detailed errors
- Keep entity IDs updated as you add/remove devices

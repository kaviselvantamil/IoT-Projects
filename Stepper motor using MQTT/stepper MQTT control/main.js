const statusDiv = document.getElementById('status');
        const valueSlider = document.getElementById('valueSlider');
        const sliderValueSpan = document.getElementById('sliderValue');

        statusDiv.textContent = 'Connecting to MQTT Broker...';

        // Connect to HiveMQ broker
        const client = mqtt.connect('wss://broker.hivemq.com:8884/mqtt');

        client.on('connect', () => {
            console.log('Connected to MQTT Broker');
            statusDiv.textContent = 'Connected to MQTT Broker';
        });

        client.on('error', (err) => {
            console.error('Connection error: ', err);
            statusDiv.textContent = 'Connection error: ' + err.message;
        });

        client.on('offline', () => {
            console.warn('Client went offline');
            statusDiv.textContent = 'MQTT Client Offline';
        });

        client.on('reconnect', () => {
            console.log('Reconnecting...');
            statusDiv.textContent = 'Reconnecting...';
        });

        // Update display value and send data when slider is adjusted
        valueSlider.addEventListener('input', function() {
            const value = valueSlider.value;
            sliderValueSpan.textContent = value;

            const topic = 'stepper01ktf'; //MQTT topic
            const message = JSON.stringify({
                value: value,
                ///////////////////
            });

            if (client.connected) {
                client.publish(topic, message, { qos: 0 }, (err) => {
                    if (err) {
                        console.error('Failed to publish message:', err);
                        statusDiv.textContent = 'Failed to publish message: ' + err.message;
                    } else {
                        console.log('Message sent:', message);
                        statusDiv.textContent = 'Message sent: ' + message;
                    }
                });
            } else {
                console.error('Client not connected');
                statusDiv.textContent = 'Client not connected';
            }
        });
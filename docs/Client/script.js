document.addEventListener('DOMContentLoaded', async (event) => {
    const joystick = document.getElementsByClassName('joystick')[0];
    const stick = document.getElementsByClassName('stick')[0];
    const radius = joystick.offsetWidth / 2; // Use half the joystick's width as radius
    let dragging = false;
    let x = 0;
    let y = 0;
    let led = 0;
    let direction = 'stopped';

    const resetStickPosition = () => {
        stick.style.top = '50%'; // Center vertically
        stick.style.left = '50%'; // Center horizontally
        stick.style.transform = 'translate(-50%, -50%)'; // Center the stick
    };

    const moveStick = (x, y) => {
        stick.style.top = `${y + radius}px`;
        stick.style.left = `${x + radius}px`;
    };

    const handleMovement = (clientX, clientY) => {
        const rect = joystick.getBoundingClientRect();
        x = clientX - rect.left - radius; // Offset to center
        y = clientY - rect.top - radius; // Offset to center

        // Calculate the distance from the center
        const distance = Math.sqrt(x * x + y * y);

        // Constrain values within the joystick radius
        if (distance > radius) {
            const angle = Math.atan2(y, x); // Get the angle to maintain direction
            x = Math.cos(angle) * radius; // Scale x to the edge of the radius
            y = Math.sin(angle) * radius; // Scale y to the edge of the radius
        }

        // Adjust for centering of the stick
        moveStick(x, y); // Move the stick immediately
    };

    // Function to calculate angle and determine direction
    function getDirection(x, y) {


        let angle = Math.atan2(y, x) * (180 / Math.PI);
         // Adjust angle to be in the range [0, 360)
        if (angle < 0) {
            angle += 360;
        }
        console.log(angle)
        direction = 'stopped';

        if (angle >= 45 && angle < 135) {
            direction = 'backward'; //inverted because it is easier this way
        } else if (angle >= 135 && angle < 225) {
            direction = 'left';
        } else if (angle >= 225 && angle < 315) {
            direction = 'forward'; //inverted because it is easier this way
        } else {
            direction = 'right'; // Covers the angle from 315 to 45
        }

        return direction;
    }

    const startDragging = (event) => {
        dragging = true;
        led = 1;

        // Handle initial movement
        handleMovement(event.touches ? event.touches[0].clientX : event.clientX,
            event.touches ? event.touches[0].clientY : event.clientY);

        //continuously sends coordinates
        
        sendInterval = setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
                let dir = getDirection(x, y)
                console.log(JSON.stringify({ dir: dir, led: led })); //debug
                socket.send(JSON.stringify({ dir: dir, led: led }));
            }
        }, 100); // Adjust the interval as needed (in milliseconds)
    };

    const stopDragging = () => {
        dragging = false;
        x = 0;
        y = 0;
        led = 0;
        direction = 'stopped';
        resetStickPosition();
    };

    const drag = (event) => {
        if (!dragging) return;
        handleMovement(event.touches ? event.touches[0].clientX : event.clientX,
            event.touches ? event.touches[0].clientY : event.clientY);
    };

    joystick.addEventListener('mousedown', startDragging);
    joystick.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', stopDragging);

    joystick.addEventListener('touchstart', startDragging, { passive: false });
    joystick.addEventListener('touchmove', drag, { passive: false });
    document.addEventListener('touchend', stopDragging);

    resetStickPosition(); // Initialize stick position

    //Initialize WebSocket connection
    let socket = new WebSocket("ws://192.168.0.211:80/direction"); //[ip]:[port]/[route]
    socket.addEventListener("open", () => {
        socket.send("Hello Server!");
    });

    /*figure out how to host web controller: open python terminal 
    python -m http.server 8000*/
});

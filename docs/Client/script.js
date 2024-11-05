document.addEventListener('DOMContentLoaded', async (event) => {
    const joystick = document.getElementsByClassName('joystick')[0];
    const stick = document.getElementsByClassName('stick')[0];
    const radius = joystick.offsetWidth / 2; // Use half the joystick's width as radius
    let dragging = false;

    const resetStickPosition = () => {
        stick.style.top = '50%'; // Center vertically
        stick.style.left = '50%'; // Center horizontally
        stick.style.transform = 'translate(-50%, -50%)'; // Center the stick
    };

    const moveStick = (x, y) => {
        stick.style.top = `${y + radius}px`;
        stick.style.left = `${x + radius}px`;
        // Send coordinates via WebSocket
        if (socket.readyState === WebSocket.OPEN) { 
            socket.send(JSON.stringify({ x, y }));
        }
    };

    const handleMovement = (clientX, clientY) => {
        const rect = joystick.getBoundingClientRect();
        let x = clientX - rect.left - radius; // Offset to center
        let y = clientY - rect.top - radius; // Offset to center

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

    const startDragging = (event) => {
        dragging = true;
        handleMovement(event.touches ? event.touches[0].clientX : event.clientX,
                       event.touches ? event.touches[0].clientY : event.clientY);
    };

    const stopDragging = () => {
        dragging = false;
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
    let socket = new WebSocket("ws://[ESP32's IP Address]:[Port #]/[Route]");
    socket.addEventListener("open", () => {
        socket.send("Hello Server!"); 
    });
});

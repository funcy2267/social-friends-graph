let waitTime = 5;
let repeatAnimation = 3;
let animationTime = 0.5;

function sleep(s) {
    return new Promise(resolve => setTimeout(resolve, s*1000));
}

let last_element;
document.addEventListener('mouseover', async function(event) {
    last_element = event.target;
    console.log(event.target);
    await sleep(waitTime);
    if (event.target==last_element) {
        event.target.classList.add(classname);
        console.log(event.target);

        for (let i = 0; i < repeatAnimation*2; i++) {
            event.target.classList.toggle(classname+'Fade');
            await sleep(animationTime);
        }
    }
});

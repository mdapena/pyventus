const texts = document.querySelectorAll(".announcement-subtitle");
let currentIndex = 0;

if (texts.length > 1) {
	setInterval(() => {
		texts[currentIndex].classList.remove("active"); // Hide current text
		currentIndex = (currentIndex + 1) % texts.length; // Move to the next text
		texts[currentIndex].classList.add("active"); // Show next text
	}, 7000); // Change text every 7 seconds
}

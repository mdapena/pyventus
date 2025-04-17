const texts = document.querySelectorAll(".announcement-subtitle");
let currentIndex = 0;

if (texts.length > 1) {
	setInterval(() => {
		texts[currentIndex].classList.remove("active"); // Hide current text
		currentIndex = (currentIndex + 1) % texts.length; // Move to the next text
		texts[currentIndex].classList.add("active"); // Show next text
	}, 5000); // Change text every 5 seconds
}

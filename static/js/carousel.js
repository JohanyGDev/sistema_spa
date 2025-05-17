const track = document.querySelector('.carousel-track');
const images = Array.from(track.children);
const prevBtn = document.querySelector('.carousel-btn.prev');
const nextBtn = document.querySelector('.carousel-btn.next');

const visibleCount = 3; 
const totalCount = images.length;
let currentIndex = 0;

function updateCarousel() {
  const imageWidth = images[0].getBoundingClientRect().width + 20; // ancho + gap
  track.style.transform = `translateX(-${currentIndex * imageWidth}px)`;
}

prevBtn.addEventListener('click', () => {
  currentIndex -= visibleCount;
  if (currentIndex < 0) currentIndex = totalCount - visibleCount;
  updateCarousel();
});

nextBtn.addEventListener('click', () => {
  currentIndex += visibleCount;
  if (currentIndex > totalCount - visibleCount) currentIndex = 0;
  updateCarousel();
});

window.addEventListener('resize', updateCarousel);

// Inicializa
updateCarousel();

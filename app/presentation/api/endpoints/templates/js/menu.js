
const menuItems = document.querySelector('.menu-items')
const menuButton = document.querySelector('.menu-icon')
const searchWrapper = document.querySelector('.search-wrapper')
const searchToggle = document.querySelector('#searchToggle')
const searchInput = document.querySelector('#searchInput')
const searchButtonSubmit = document.querySelector('.search-submit-btn')

menuButton.addEventListener('click', () => {
    // e.stopPropagation();
    menuItems.classList.add('active')
})

document.addEventListener('click', (e) => {
    if (!menuItems.contains(e.target) && !menuButton.contains(e.target)) {
        menuItems.classList.remove('active')
    }
})

searchToggle.addEventListener('click', function() {
    if (searchInput.classList.contains('active')) {
        this.closest('form').submit();
    } else {
        searchInput.classList.add('active');
        searchInput.focus()
    }
})

document.addEventListener('click', (e) => {
    if (!searchWrapper.contains(e.target)) {
        searchInput.classList.remove('active')
    }
})


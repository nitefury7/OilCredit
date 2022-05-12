

function toggle_sidebar() {
    function getStyle(element, name) {
        return element.currentStyle ? element.currentStyle[name] : window.getComputedStyle ? window.getComputedStyle(element, null).getPropertyValue(name) : null;
    }
    sidebar = document.getElementById('sidebar');
    main = document.getElementById('main');
    if (sidebar && main) {
        if (getStyle(sidebar, 'display') === 'none') {
            sidebar.style.display = 'block';
            main.style.overflow = 'hidden';
        } else {
            sidebar.style.display = 'none';
            main.style.overflow = 'auto';
        }
    }
}

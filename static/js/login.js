/*
Elements
 */
const showPasswordToggle = document.querySelector('.show-password-toggle')


/*
Functions
 */
function handlePasswordToggle() {
    if (showPasswordToggle.textContent === 'SHOW') {
        showPasswordToggle.textContent = 'HIDE'
        passwordField.setAttribute('type', 'text')
    } else {
        showPasswordToggle.textContent = 'SHOW'
        passwordField.setAttribute('type', 'password')
    }
}


/*
Event listeners
 */
showPasswordToggle.onclick = function (e) {
    e.preventDefault()

    handlePasswordToggle()

    return false
}
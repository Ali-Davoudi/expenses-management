/*
Elements
 */
const usernameField = document.querySelector('#username-field')
const usernameFeedbackArea = document.querySelector('.validate-username-feedback')
const emailField = document.querySelector('#email-field')
const emailFeedbackArea = document.querySelector('.validate-email-feedback')
const usernameChecking = document.querySelector('.username-checking')
const emailChecking = document.querySelector('.email-checking')
const showPasswordToggle = document.querySelector('.show-password-toggle')
const passwordField = document.querySelector('#password-field')
const btnSubmit = document.querySelector('.btn-submit')


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
usernameField.addEventListener('keyup', (e) => {
    console.log('test')

    // Earning the username field value
    const usernameVal = e.target.value

    // Only show up 'Checking' word when username field is not empty
    if (usernameVal.length > 0) {
        usernameChecking.style.display = "block"
        usernameChecking.textContent = `Checking ${usernameVal}`
    }

    // Remove some classes and modify styles when fetching the data according to the result
    usernameField.classList.remove('is-invalid')
    usernameField.classList.remove('is-valid')
    usernameFeedbackArea.classList.remove('invalid-feedback')
    usernameFeedbackArea.classList.remove('valid-feedback')
    usernameFeedbackArea.style.display = "none"

    if (usernameVal.length > 0) {
        fetch('/auth/validate-username/', {
            body: JSON.stringify({'username': usernameVal}),
            method: 'POST'
        }).then(res => res.json()).then(data => {
            console.log('data: ', data)
            usernameChecking.style.display = "none"

            if (data.username_error) {
                usernameField.classList.add('is-invalid')
                usernameFeedbackArea.classList.add('invalid-feedback')
                usernameFeedbackArea.style.display = "block"
                usernameFeedbackArea.innerHTML = `<p>${data.username_error}</p>`
                btnSubmit.disabled = true
            } else {
                usernameField.classList.add('is-valid')
                usernameFeedbackArea.classList.add('valid-feedback')
                usernameFeedbackArea.style.display = "block"
                usernameFeedbackArea.innerHTML = '<p>Looks good!</p>'
                btnSubmit.removeAttribute('disabled')
            }
        })
    }
})

emailField.addEventListener('keyup', (e) => {
    console.log('test email')

    // Earning the email field value
    const emailVal = e.target.value

    // Only show up 'Checking' word when username field is not empty
    if (emailVal.length > 0) {
        emailChecking.style.display = "block"
        emailChecking.textContent = `Checking ${emailVal}`
    }

    // Remove some classes and modify styles when fetching the data according to the result
    emailField.classList.remove('is-invalid')
    emailField.classList.remove('is-valid')
    emailFeedbackArea.classList.remove('invalid-feedback')
    emailFeedbackArea.classList.remove('valid-feedback')
    emailFeedbackArea.style.display = "none"

    if (emailVal.length > 0) {
        fetch('/auth/validate-email/', {
            body: JSON.stringify({'email': emailVal}),
            method: 'POST'
        }).then(res => res.json()).then(data => {
            console.log('email data: ', data)
            emailChecking.style.display = "none"

            if (data.invalid_email) {
                emailField.classList.add('is-invalid')
                emailFeedbackArea.classList.add('invalid-feedback')
                emailFeedbackArea.style.display = "block"
                emailFeedbackArea.innerHTML = `<p>${data.invalid_email}</p>`
                btnSubmit.disabled = true
            } else {
                emailField.classList.add('is-valid')
                emailFeedbackArea.classList.add('valid-feedback')
                emailFeedbackArea.style.display = "block"
                emailFeedbackArea.innerHTML = '<p>Looks good!</p>'
                btnSubmit.removeAttribute('disabled')
            }
        })
    }
})

showPasswordToggle.onclick = function (e) {
    e.preventDefault()

    handlePasswordToggle()

    return false
}
/*
    Elements
 */

const searchField = document.querySelector('#searchField')
const tableOutput = document.querySelector('.table-output')
const appTable = document.querySelector('.app-table')
const paginationContainer = document.querySelector('.pagination-container')
const tableBody = document.querySelector('.table-body')
const noResults = document.querySelector('.no-results');

/*
    Styles
 */

tableOutput.style.display = 'none'


/*
    Functions
 */

function getCookie(name) {
    var cookieValue = null

    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';')

        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim()

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))

                break
            }
        }
    }

    return cookieValue
}

function realTimeSearch(searchText) {
    console.log(searchText)

    fetch('/search-expense/', {
        body: JSON.stringify({'searchText': searchText}),
        method: 'POST',
        headers: {'X-CSRFToken': getCookie('csrftoken')}
    }).then(res => res.json()).then(data => {
        console.log('data: ', data)

        appTable.style.display = 'none'
        tableOutput.style.display = 'block'

        if (data.length === 0) {
            noResults.style.display = 'block'
            tableOutput.style.display = 'none'
        } else {
            noResults.style.display = 'none'
            data.forEach(
                (item) => {
                    tableBody.innerHTML +=
                        `
                        <tr>
                            <td>${item.amount}</td>
                            <td>${item.description}</td>
                            <td>${item.category}</td>
                            <td>${item.date}</td>                        
                        </tr>
                        `
                }
            )
        }
    })
}

/*
    Event listeners
 */

searchField.onkeyup = function (e) {
    const searchValue = e.target.value

    if (searchValue.trim().length > 0) {
        realTimeSearch(searchValue)
        paginationContainer.style.display = 'none'
        tableBody.innerHTML = ''
    } else {
        tableOutput.style.display = 'none'
        appTable.style.display = 'block'
        paginationContainer.style.display = 'block'
    }
}
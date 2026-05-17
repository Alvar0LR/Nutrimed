function decidirCookies(decision) {
  document.getElementById('cookie-banner').style.display = 'none'

  fetch('/cookies/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]') 
        ? document.querySelector('[name=csrfmiddlewaretoken]').value 
        : window.csrfToken
    },
    body: 'decision=' + decision
  })
}

document.addEventListener('DOMContentLoaded', function() {
  if (typeof window.cookiesDecididas !== 'undefined' && !window.cookiesDecididas) {
    setTimeout(function() {
      const banner = document.getElementById('cookie-banner')
      if (banner) banner.style.display = 'flex'
    }, 1000)
  }
})
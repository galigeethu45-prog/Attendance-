function getCSRFToken() {
return document.querySelector('meta[name="csrf-token"]').getAttribute("content")
}
document.addEventListener("DOMContentLoaded", () => {

const loginSection = document.getElementById("login-section")
const registerSection = document.getElementById("register-section")

const showRegisterBtn = document.getElementById("show-register")
const showLoginBtn = document.getElementById("show-login")

showRegisterBtn.onclick = () => {
loginSection.classList.add("hidden")
registerSection.classList.remove("hidden")
}

showLoginBtn.onclick = () => {
registerSection.classList.add("hidden")
loginSection.classList.remove("hidden")
}


document.getElementById("loginApiForm")
.addEventListener("submit", async function(e){

e.preventDefault()

const identifier =
document.getElementById("identifier").value

const password =
document.getElementById("password").value

try{

const response = await fetch("/api/login/",{

method:"POST",
headers:{
"Content-Type":"application/json",
"X-CSRFToken": getCSRFToken()
},

body:JSON.stringify({
identifier:identifier,
password:password
})

})

const data = await response.json()

if(response.ok){

alert("Login successful")

window.location.href="/dashboard"

}else{

document.getElementById("loginError")
.innerText=data.error || "Login failed"

}

}catch{

document.getElementById("loginError")
.innerText="Server error"

}

})



document.getElementById("registerApiForm")
.addEventListener("submit", async function(e){

e.preventDefault()

const employee_id =
document.getElementById("regEmployeeId").value

const email =
document.getElementById("regEmail").value

const password =
document.getElementById("regPassword").value

try{

const response = await fetch("/api/register/",{

method:"POST",
headers:{
"Content-Type":"application/json",
"X-CSRFToken": getCSRFToken()
},

body:JSON.stringify({
employee_id:employee_id,
email:email,
password:password
})

})

const data = await response.json()

if(response.ok){

alert("Registration successful. Please login.")

registerSection.classList.add("hidden")
loginSection.classList.remove("hidden")

}else{

document.getElementById("registerError")
.innerText=JSON.stringify(data)

}

}catch{

document.getElementById("registerError")
.innerText="Server error"

}

})

})
var modal = document.getElementById("modalcreate");

// Get the button that opens the modal
var btn = document.getElementById("triggercreate");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

function addCountry() {
  var countryInput = document.getElementById("country");
  var countryList = document.getElementById("countryList");
  var countryName = countryInput.value.trim();
  if (countryName !== "") {
    var newCountry = document.createElement("li");
    newCountry.innerHTML = countryName + ' <button onclick="removeItem(this)">Remove</button>';
    countryList.appendChild(newCountry);
    countryInput.value = "";
  } else {
    alert("Country name cannot be empty.");
  }
}

function addUser() {
  var userInput = document.getElementById("authusers");
  var userList = document.getElementById("userList");
  var userName = userInput.value.trim();
  if (userName !== "") {
    var newUser = document.createElement("li");
    newUser.innerHTML = userName + ' <button onclick="removeItem(this)">Remove</button>';
    userList.appendChild(newUser);
    userInput.value = "";
  } else {
    alert("User name cannot be empty.");
  }
}

function removeItem(button) {
  var li = button.parentElement;
  li.parentElement.removeChild(li);
}

document.getElementById('createCommitteeForm').addEventListener('submit', function(event) {
  event.preventDefault();
  
  const committeeName = document.getElementById('committeename').value;
  
  const countryList = document.getElementById('countryList');
  const countries = Array.from(countryList.children).map(li => li.textContent.replace(' Remove', '')).join(', ');

  const userList = document.getElementById('userList');
  const users = Array.from(userList.children).map(li => li.textContent.replace(' Remove', '')).join(', ');
  
  const newCommitteeBox = document.createElement('div');
  newCommitteeBox.className = 'committeebox';
  newCommitteeBox.innerHTML = `<h3>${committeeName}</h3><p>Countries: ${countries}</p><p>Authorized Users: ${users}</p><input class="enterbutton" type="button" value="Enter">`;
  
  document.getElementById('committeeboxholder').appendChild(newCommitteeBox);
  
  document.querySelector('.close').click();
  event.target.reset();
  countryList.innerHTML = '';
  userList.innerHTML = '';
});
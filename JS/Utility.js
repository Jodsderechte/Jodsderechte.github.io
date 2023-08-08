var mySidebar;
let WebsiteUrl = "https://florian-reichle.de"

window.onload = function(){
    let form = document.querySelector("#language-picker-select")
    form.addEventListener("change", function(event){
      handleLanguage(form.options[form.selectedIndex].lang);
     })
    mySidebar = document.getElementById("mySidebar");
    let language = localStorage.getItem('language') || navigator.language || navigator.userLanguage || 'en-US';
    handleLanguage(language); //setting language
}

  
  
  // Toggle between showing and hiding the sidebar when clicking the menu icon
  
  function w3_open() {
    if (mySidebar.style.display === 'block') {
      mySidebar.style.display = 'none';
    } else {
      mySidebar.style.display = 'block';
    }
  }
  
  // Close the sidebar with the close button
  function w3_close() {
      mySidebar.style.display = "none";
  }
  
  //Language Picker
  
  let languageConverter = {
    "en-US":"english",
    "de-DE":"deutsch",
  }
  let languageCodeConverter ={
    "english":"en",
    "deutsch":"de",
  }
  let currentLanguage
  function handleLanguage(language){
    if(!currentLanguage || language!= currentLanguage){
      console.log("changing language");
      if(!languageConverter[language]){
        language = "en-US";
      }
      $.ajax({ url: WebsiteUrl+"/Translations/"+language+".json",dataType: "json", success: function( response ) { 
        console.log("Language changed to: " + language);
        document.querySelector("#language-picker-select").value = languageConverter[language];
        currentLanguage = language;
        localStorage.setItem('language', language);
        document.documentElement.setAttribute("lang", language.match(/(.*?)(?=-)/)[1]);
        document.title = response["WhoAmI"];
        for (const key in response){
          var elements = document.getElementsByClassName(key);
          for(var i = 0; i < elements.length; i++) {
            elements[i].innerHTML = response[key];
          }
        }
    }})  
    }
  }

  
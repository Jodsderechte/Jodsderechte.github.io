var mySidebar;
window.onload = function(){
    let form = document.querySelector("#language-picker-select")
    form.addEventListener("change", function(event){
      handleLanguage(form.options[form.selectedIndex].lang);
     })
     mySidebar = document.getElementById("mySidebar");
}




// Modal Image Gallery
function onClick(element) {
    //document.getElementById("img01").src = element.src;
    var captionText = document.getElementById("modalIframe");
    captionText.src = element.alt;
    setTimeout(() => { document.getElementById("modal01").style.display = "block";} ,50);
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
  const map = [
      { suffix: 'M', threshold: 1e6 },
      { suffix: 'K', threshold: 1e3 },
      { suffix: '', threshold: 1 },
    ];
  function kFormatter(num,precision) {
    const found = map.find((x) => Math.abs(num) >= x.threshold);
    if (found) {
      if (found.suffix == 'M' || num < 99999){
        const formatted = (num / found.threshold).toFixed(precision) + found.suffix;
        return formatted;
      }
      else{
        const formatted = (num / found.threshold).toFixed(0) + found.suffix;
      return formatted;
      }
    }
  
    return num;
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
      $.ajax({ url: "https://jods.me/Translations/"+language+".json",dataType: "json", success: function( response ) { 
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
  
  // Auto generation of Dungeon Aura Entries
  let WeakAurasTable = [
  {
      "urlname": "DF-Dungeons",
      "query" : "#DragonflightDungeonsVersion",
      "img" : "/images/DragonflightDungeons.JPG",
      "name" : "Dragonflight",
      "expansion" : "Dragonflight",
      "order" : 1,
    },  
  {
      "urlname": "SL-Dungeons",
      "query" : "#ShadownlandsDungeonsVersion",
      "img" : "/images/ShadowlandsDungeons.JPG",
      "name" : "Shadowlands",
      "expansion" : "Shadowlands",
      "order" : 2,
  },
  {
      "urlname": "BFA-Dungeons",
      "query" : "#BattleForAzerothDungeonsVersion",
      "img" : "/images/BattleForAzerothDungeons.JPG",
      "name" : "Battle for Azeroth",
      "expansion" : "Battle for Azeroth",
      "order" : 3,
  },
  {
      "urlname": "Legion-Dungeons",
      "query" : "#LegionDungeonsVersion",
      "img" : "/images/LegionDungeons.JPG",
      "name" : "Legion",
      "expansion" : "Legion",
      "order" : 4,
  },
  {
      "urlname": "WOD-Dungeons",
      "query" : "#WODDungeonsVersion",
      "img" : "/images/DraenorDungeons.JPG",
      "name" : "Draenor",
      "expansion" : "Warlords of Draenor",
      "order" : 5,
  },
  {
      "urlname": "MOP-Dungeons",
      "query" : "#MOPungeonsVersion",
      "img" : "/images/PandariaDungeons.JPG",
      "name" : "Pandaria",
      "expansion" : "Mists of Pandaria",
      "order" : 6,
  },
  {
      "urlname": "Cataclysm-Dungeons",
      "query" : "#CataclysmDungeonsVersion",
      "img" : "/images/CataclysmDungeons.JPG",
      "name" : "Cataclysm",
      "expansion" : "Cataclysm",
      "order" : 7,
  },
  ]
  let WeakauraViews = WeakauraInstalls =WeakauraFavorites = WeakauraComments =0;
  $(document).ready(function(){
    WeakAurasTable.forEach(element => {
      $.ajax({ url: "https://data.wago.io/api/check/weakauras?ids="+element.urlname,dataType: "json", success: function( response ) {
        let ParentDiv = document.createElement("div")
        ParentDiv.className="w3-col l3 m6 w3-margin-bottom"
        ParentDiv.id = element.order
  
        let cardDiv = document.createElement("div")
        cardDiv.className="w3-card"
        ParentDiv.appendChild(cardDiv)
  
        let img = document.createElement("img")
        img.src= element.img
        img.style="width:100%"
        cardDiv.appendChild(img)
  
        let TextContainer = document.createElement("div")
        TextContainer.className="w3-container"
        cardDiv.appendChild(TextContainer)
  
        let h3div = document.createElement("div")
        h3div.className = "DungeonTitle"
        TextContainer.appendChild(h3div)
  
        let h3 = document.createElement("h3")
        h3.innerHTML = element.name
        h3div.appendChild(h3)
  
        let pTitle = document.createElement("div")
        pTitle.className="w3-opacity"
        pTitle.innerHTML = response[0].versionString &&"Version: "+response[0].versionString || "Mtyhic + Dungeons"
        pTitle.id = element.query
        TextContainer.appendChild(pTitle)
  
        let pbutton = document.createElement("p")
        let button = document.createElement("button")
        let buttonImg = document.createElement("img")
        pbutton.appendChild(button)
        buttonImg.src="/images/wago.io.png"
        buttonImg.width="50"
        buttonImg.height="30"
        button.appendChild(buttonImg)
        button.innerHTML = button.innerHTML + " Get it on wago"
        button.className="w3-button w3-dark-grey w3-block"
        button.onclick = function(){window.location.href='https://wago.io/'+element.urlname;}
        TextContainer.appendChild(pbutton)
        
        if (document.querySelector("#WeakAurasList").lastChild && document.querySelector("#WeakAurasList").lastChild.id > ParentDiv.id){
          $('#WeakAurasList').find('div').each(function(index,element){
            if (ParentDiv.id < element.id){
              document.querySelector("#WeakAurasList").insertBefore(ParentDiv, element)
              return false;
            }
          })
        }else{
          document.querySelector("#WeakAurasList").appendChild(ParentDiv)
        }
      }})
    });
    // Requesting of Weakaura Data for CoreAuras and Views/Installs etc.
    $.ajax({ url: "https://data.wago.io/api/check/weakauras?ids=f7Z1Te6hb",dataType: "json", success: function( response ) {document.querySelector("#InterruptTrackerVersion").innerHTML = "Version: "+response[0].versionString;}})
    $.ajax({ url: "https://data.wago.io/api/check/weakauras?ids=NyseKq1Xo",dataType: "json", success: function( response ) {document.querySelector("#RaidAbilityTimelineVersion").innerHTML = "Version: "+response[0].versionString;}})
    $.ajax({ url: "https://jods.me/Data/WaList_Converted.json",dataType: "json", success: function( response ) { 
      //WeakauraViews = WeakauraViews+response.viewCount; document.querySelector(".TotalWeakAuraViews").innerHTML = WeakauraViews;
      console.log(response)
      console.log(response.length)
      for (let index = 0; index < response.length; index++) {
        let element = response[index];
        $.ajax({ url: "https://jods.me/Data/WeakAuras/"+element+".json",dataType: "json", success: function( response ) {
          WeakauraViews = WeakauraViews+response.viewCount; 
          WeakauraInstalls = WeakauraInstalls+response.installCount;
          WeakauraFavorites = WeakauraFavorites+response.favoriteCount
          WeakauraComments = WeakauraComments+response.commentCount
          document.querySelector(".TotalWeakAuraViews").innerHTML = kFormatter(WeakauraViews,2); 
          document.querySelector(".TotalWeakAuraInstalls").innerHTML = kFormatter(WeakauraInstalls,2);
          document.querySelector(".TotalWeakAuraFavorites").innerHTML = kFormatter(WeakauraFavorites,1);
          document.querySelector(".TotalWeakAuraComments").innerHTML = kFormatter(WeakauraComments,1);
        }})
  
      }
    }})
    let language = localStorage.getItem('language') || navigator.language || navigator.userLanguage || 'en-US';
    handleLanguage(language); //setting language
  })
  
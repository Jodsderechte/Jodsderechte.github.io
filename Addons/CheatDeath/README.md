[![Discord][SVG-Discord]][Discord]
[![PayPal][SVG-PayPal]][PayPal]
[![Curseforge][SVG-Curseforge]][Curseforge]


This mod is the ASA version of DinoCheatDeath and offers a simple replacement for Ark's Homing Pigeon mod.  

An item that can be crafted to give your dinosaur an extraordinary ability to cheat death. When faced with certain demise, this item activates, granting your beloved creature a remarkable second chance at life.  

It introduces a deployable structure where your dinosaur can be transported to in two scenarios: when it gets killed or when its rider/last rider perishes (though this feature can be disabled if desired through the .ini options) alternatively you can recall the Dino at any flag and it will transport your Dino right to you.  

This mechanism operates by temporarily rendering the dinosaur immune to harm for a duration of 5 seconds if it's rider, or they die. To maintain balance, a 30-minute cooldown is in place (which can be customized through the .ini options).  


### Config options. (time is in seconds)  
```yml
[DinoCheatDeath]  
InvincibleDuration=5  
CheatDeathCooldown=1800  
TeleportOnDinoDeath=True  
TeleportOnPlayerDeath=True  
ActivateDebugPrints = false  
```
These values can be adjusted to suit your preferences through the .ini options.  
  
### SpawnCommands:  

+ CheatDeathFlag:
```
cheat giveitem "/CheatDeath/Items/PrimalItemStructure_DinoCheatDeath_Flag.PrimalItemStructure_DinoCheatDeath_Flag" 10 0 0 false  
```
+ CheatDeathConsumable:
```
 cheat giveitem "/CheatDeath/Items/PrimalItem_DinoCheatDeath_Consumable.PrimalItem_DinoCheatDeath_Consumable" 10 0 0 false  
```  
I would like to extend my special thanks to the Ark modding community on Discord, particularly Quellcast, Pullourpo, and joehelp, whose guidance and assistance were instrumental in helping me navigate the intricacies of the ArkDevKit and kick-starting this project.  

[//]: # (Links)

[Discord]: https://discord.com/invite/v3gYmYamGJ (Join the Discord)
[PayPal]: https://www.paypal.com/donate/?hosted_button_id=PSQ4D3HXNZKMG (Donate via PayPal)
[Curseforge]: https://www.curseforge.com/ark-survival-ascended/mods/autodoors

[//]: # (Images)
[SVG-Curseforge]: https://cf.way2muchnoise.eu/short_931047.svg
[SVG-Discord]: https://img.shields.io/badge/Discord-7289da?logo=discord&logoColor=fff&style=flat-square
[SVG-PayPal]: https://custom-icon-badges.demolab.com/badge/-Donate-lightgrey?style=flat-square&logo=paypal&color=007CB1

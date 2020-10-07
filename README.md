# Corona-radar
Skill-ID amzn1.ask.skill.a6d7d659-d846-4c73-a727-87d6b5b619ed

An Alexa VUI to interact with data from the following APIs:

https://coronavirusapi.com/ <br/>
https://www.nytimes.com/interactive/2020/us/coronavirus-us-cases.html

The user can ask questions like

| User request  | Alexa response | 
| --------  | ------------------- | 
| What are the latest numbers in my area? | In {device location's} county {US state}, {number}, people have died and there are {number} existing cases of coronavirus      | 
| How many deaths from coronavirus in {US state}?      | {US state} has had deaths from coronavirus |
| What are the top {number} states with covid? | {US state} with {num} deaths [repeats] for {number}      | 
| List the bottom {number} states with coronavirus      | {US state} with {num} deaths [repeats] for {number}|


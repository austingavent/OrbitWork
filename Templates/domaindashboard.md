---
object: domaindashboard
created: <% tp.date.now("YYYY-MM-DD") %>
domain: <% tp.file.title %>
track_number: 7
---
`BUTTON[satdir, orbdir, yamlnote]` 
# <% tp.file.title %> Dashboard

## Overview
Notes


`$=dv.list(dv.pages().filter(p => p.object === "project" && p.file.folder.includes(dv.current().file.folder)).sort(p => p.file.name).map(p => p.file.link + " (Created: " + moment(p.created).format("YYYY-MM-DD") + ")"))`







## Designated Projects
* 📋 Sub-Projects `BUTTON[satdir]`  `$=dv.list(dv.pages().filter(p => p.object === "project" && p.file.folder.includes(dv.current().file.folder)).sort(p => p.file.name).map(p => p.file.link + " (Created: " + p.created + ")"))`



## Inbox Projects
* 📥 Parent Projects <button class="metabind-inline-btn" data-template="Create Orbiting Directory">+Directory</button> `$=dv.list(dv.pages().filter(p => p.object === "project" && p.file.folder.includes(dv.current().file.folder + "/.0-inbox")).sort(p => p.file.name).map(p => p.file.link + " (Created: " + p.created + ")"))`

## Notes in Inbox
* 📝 Recent Inbox Notes <button class="metabind-inline-btn" data-template="C1yaml">+Note</button> `$=dv.list(dv.pages().filter(p => p.object !== "project" && p.object !== "domain" && p.file.folder.includes(dv.current().file.folder + "/.0-inbox")).sort(p => p.created, "desc").limit(10).map(p => p.file.link + " | Object: " + p.object + " | Projects: " + (p.orbits || "None") + " | Created: " + p.created))`

## Recent Activity
* 🔄 Latest Updates `$=dv.list(dv.pages().filter(p => p.object !== "project" && p.object !== "domain" && p.file.folder.includes(dv.current().file.folder)).sort(p => p.created, "desc").limit(10).map(p => p.file.link + " | Object: " + p.object + " | Projects: " + (p.orbits || "None") + " | Created: " + p.created))`

<!-- Add this CSS to style your buttons -->

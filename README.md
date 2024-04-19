# Kuma Browser

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./resources/white.png">
  <source media="(prefers-color-scheme: light)" srcset="./resources/black.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="./resources/black.png" align="right" width="40%">
</picture>

Kuma Browser enables a few functionalities from the [jpdb.io](jpdb.io) search engine directly within Anki.

> [!CAUTION]
> Kuma Browser is not an official JPDB addon. It simply aims to facilitate the creation of Anki cards, but does not want to replace JPDB. 
> 
> People from JPDB if you see this, please make an offline app for your website 🖤🤍

> [!NOTE]
> Kuma Browser is a project in development, and features are added when I need them. 
> You can contribute by [adding an Issue](https://github.com/Raffaelbdl/kuma-browser/issues/new) or making a Pull Request.

## Installation
The installation process is similar to other Anki plugins and can be accomplished in three steps:

1) Download the latest release's .zip file
2) Select `Tools` → `Add-ons`, then click on `View Files`
3) Drag the downloaded .zip file in the `addons21` folder, and unzip it

## Features
To start the Kuma Browser, select `Tools` → `Kuma Browser`

### The Search Tab

- The `Search`　tab allows to quicly search a word through a deck.

- Selecting an item will open the corresponding `Edit` window, to quickly make modifications.

- Right-clicking on an item makes a context menu open:
  - `Study Next` will set the `due` position to zero if the cards are *New*.
  
### The JPDB Tab

- The `JPDB` tab works as a substitute to [jpdb.io](jpdb.io) search engine.

- Double-clicking an item will open the corresponding JPDB page.

- `Generate Note` will create the note associated to the JPDB entry.

### The JPDB Vocabulary List Tab

- The `JPDB VocabList` tab allows to create Anki notes from JPDB vocabulary lists.

- You can enter a link of a vocabulary list, eg. `https://jpdb.io/novel/5829/kuma-kuma-kuma-bear/vocabulary-lis` and click `Search vocab list on JPDB` to see what notes will be created.
  
- `Generate all notes` will create all the notes of the search result.

- Note existence is checked based on the Expression field, which might not be sufficient to fully separate JPDB entries in practice.

### Provided Template

I provide my own template, but it can be freely modified from the `config/` folder.

![kuma](./resources/kuma.png)


*You can change between くまきゅう and くまゆる by using light or dark theme.*

# Kuma Browser

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./resources/white.png">
  <source media="(prefers-color-scheme: light)" srcset="./resources/black.png">
  <img alt="Shows Kumakyuu in dark mode and Kumayuru in light mode." src="./resources/black.png" align="right" width="40%">
</picture>

[**Installation**](#installation) |
[**Features**](#features) |
[**Common Issues**](#common-issues) |


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

### The Reposition Tab

- The `Reposition` tab allows to reposition cards based on the frequency field for a given deck.

- Only the `New` cards will be repositioned.

### The JPDB API Vocabulary List Tab

- The `JPDB VocabList` tab allows to create Anki notes from JPDB vocabulary lists using the JPDB API.
  
- This way is faster and more reliable than the normal one, but it does not provide example sentences.

- Usage:
  - Log into your JPDB account
  - In `Settings` get your API key at the bottom of the page.
  - In `Learn(x)` click on the vocabulary list you want to add, and get the Id at the end of the url.
  - In Anki, enter the information and press `Generate`.

- Note existence is checked based on the Expression field, which might not be sufficient to fully separate JPDB entries in practice.
  
- You can save your API key by toggling the check box.


### Provided Template

I provide my own template, but it can be freely modified from the `config/` folder.

![kuma](./resources/kuma.png)


*You can change between くまきゅう and くまゆる by using light or dark theme.*

## Common Issues

### JPDB Vocabulary List Tab fails

This method to create notes is known to fail a lot. It is supposedly due to jpdb.io restricting users so that they cannot do too many requests too fast 😶 ([#18](https://github.com/Raffaelbdl/kuma-browser/issues/18)). If it happens, you may have been temporarily banned. Wait a bit before trying either the JPDB Vocabulary List scraper or the JPDB Vocabulary List API. 

One way to solve this is to use the API: it should not be limited like the web scraping method.

If you want the example sentences however, you will need to set a delay between each requests. This can be done by setting the parameter `sleep_time` in `config/vl.json`. For example:

```json
{ "sleep_time": 0.1 }
```

Do not change the key `sleep_time` as there is no self-repair mechanism 😆
# Что представляет собой этот телеграмм-бот.
В него подключена MySql и json(на самом деле это была моя огромная ошибка).

В нем присутствует: регистрация, авторизация и игра - Double.
![image](https://user-images.githubusercontent.com/88852824/180061907-d1a063ba-4ca7-480c-8533-5be18d3ff794.png)
![image](https://user-images.githubusercontent.com/88852824/180062025-1c3ddaa5-6224-4bf9-bfd7-22c5f998ea9a.png)
![image](https://user-images.githubusercontent.com/88852824/180062716-93eac116-8510-4795-9a31-e7c7f8b49076.png)

Объясняю, почему подключение json стала для меня большой ошибкой. Что вообще представляет мой json файл: {email: {information:{'money': money, 'create_data': create_data}}}. И это ужасно. Если кто-то захочет реализовать таблицу топов с использованием этого json в этом боте, то её либо не сделать, либо очень тяжело(для меня был выбор - не сделать).

Как надо было сделать: создать новую таблицу, которая напрямую будет взаимодействовать с почтой и всё. РЕБЯТ И ВСЁ. Я не знаю почему я, до этого не додумался. И еще, если кто-то и будет брать этот код, то исправьте данное недоразумение. И да я знаю, что у меня код очень массивный и неаккуратный, я не знал как мне это реализовать, да и сейчас не знаю. Так что не пинайте, извините.

# What is this telegram bot.
MySQL and json are connected to it (in fact, it was my huge mistake).

It contains: registration, authorization and game - Double.

I explain why connecting json was a big mistake for me. What is my json file in general: {email: {information:{'money': money, 'create_data': create_data}}}. And it's terrible. If someone wants to implement a table of tops using this json in this bot, then it is either not done, or it is very difficult (for me there was a choice - not to do).

How to do it: create a new table that will directly interact with mail and that's it. GUYS AND THAT'S IT. I don't know why I didn't think of that. And yet, if someone will take this code, then correct this misunderstanding. And yes, I know that my code is very massive and sloppy, I didn't know how to implement it, and even now I don't know. So don't kick, sorry.

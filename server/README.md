# Бекенд для сайта

Апи, обработка запросов

## Формат конфиг-файла:

```ini
[Flask]
// Ключ-конфига-для-Flask = значение-конфига-для-Flask
// Пример:
SECRET_KEY = ....
SQLALCHEMY_DATABASE_URI = sqlite:///database.db
SQLALCHEMY_TRACK_MODIFICATIONS = False

[RunConfig]
host = ...
port = ...
debug = ...
```

## Структура базы данных:

### User

* `id`: Integer
* `first_name`: String(80)
* `last_name`: String(80)
* `username`: String(80)
* `password_hash`: String(64)
* `description`: String(400)
* `channels`: List[[Channel](#channel)]
* `membership`: List[[ChannelMember](#channelmember)]
* `messages`: List[[Message](#message)]
* `friends`: List[[User](#user)]
* `user_roles`: List[[UserRole](#userrole)]
* `user_invitations`: List[[ChannelInvitation](#channelinvitation)]

### Channel

* `id`: Integer
* `title`: String(80)
* `description`: String(400)
* `default_role_id`: Integer
* `members`: List[[ChannelMember](#channelmember)]
* `messages`: List[[Message](#message)]
* `roles`: List[[ChannelRole](#channelrole)]
* `user_roles`: List[[UserRole](#userrole)]
* `member_invitations`: List[[ChannelInvitation](#channelinvitation)]

### ChannelInvitation

* `id`: Integer
* `user`: [User](#user)
* `channel`: [Channel](#channel)

### ChannelRole

* `id`: Integer
* `role_name`: String(80)
* `watch_channel_information_permission`: Boolean
* `watch_channel_members_permission`: Boolean
* `read_channel_permission`: Boolean
* `send_messages_permission`: Boolean
* `edit_channel_permission`: Boolean
* `user_roles`: List[[UserRole](#userrole)]
* `channel`: Channel

### ChannelMember

* `id`: Integer
* `user`: [User](#user)
* `channel`: [Channel](#channel)

### UserRole

* `id`: 
* `user`: [User](#user)
* `role`: [ChannelRole](#channelrole)
* `channel`: [Channel](#channel)

### Message

* `id`: Integer
* `text`: String(2000)
* `datetime`: DateTime
* `channel`: Channel
* `author`: [User](#user)

## Структура API:

### User API (`/api/user`)

#### *GET* `/get_client_user`

> *Parameters*: Нет
> 
> *Login required*: _True_

#### *GET* `/get_user`

> *Parameters*:
> * `user_id` (_required_)
> 
> *Login required*: _False_

#### *POST* `/update_profile`

> *Parameters*:
> * `first_name` (_not required, not blank_)
> * `last_name` (_not required, not blank_)
> * `description` (_not required, may be blank_)
> 
> *Login required*: _True_

#### *POST* add_friend

> *Parameters*:
> * `user_id` (_required_)
> 
> *Login required*: _True_

#### *POST* `/remove_friend`

> *Parameters*:
> * `user_id` (_required_)
> 
> *Login required*: _True_


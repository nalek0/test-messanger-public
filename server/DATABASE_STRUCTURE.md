# Структура базы данных

## User

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

## Channel

* `id`: Integer
* `title`: String(80)
* `description`: String(400)
* `default_role_id`: Integer
* `members`: List[[ChannelMember](#channelmember)]
* `messages`: List[[Message](#message)]
* `roles`: List[[ChannelRole](#channelrole)]
* `user_roles`: List[[UserRole](#userrole)]
* `member_invitations`: List[[ChannelInvitation](#channelinvitation)]

## ChannelInvitation

* `id`: Integer
* `user`: [User](#user)
* `channel`: [Channel](#channel)

## ChannelRole

* `id`: Integer
* `role_name`: String(80)
* `watch_channel_information_permission`: Boolean
* `watch_channel_members_permission`: Boolean
* `read_channel_permission`: Boolean
* `send_messages_permission`: Boolean
* `edit_channel_permission`: Boolean
* `user_roles`: List[[UserRole](#userrole)]
* `channel`: Channel

## ChannelMember

* `id`: Integer
* `user`: [User](#user)
* `channel`: [Channel](#channel)

## UserRole

* `id`: 
* `user`: [User](#user)
* `role`: [ChannelRole](#channelrole)
* `channel`: [Channel](#channel)

## Message

* `id`: Integer
* `text`: String(2000)
* `datetime`: DateTime
* `channel`: Channel
* `author`: [User](#user)

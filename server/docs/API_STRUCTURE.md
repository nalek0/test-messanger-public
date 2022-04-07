# Структура API 

## User API (`/api/user`)

### **[POST]** `/get`

#### Parameters:

* `user_id` (_required_)

#### Login required:
_False_

### **[POST]** `/client/get`

#### Parameters:
No

#### Login required:
_True_

### **[POST]** `/client/signup`

#### Parameters:

* `first_name` (_required, not blank_)
* `last_name` (_required, not blank_)
* `username` (_required, unique_)
* `password` (_required_)

#### Login required:
_False_

### **[POST]** `/client/login`

#### Parameters:

* `username` (_required_)
* `password` (_required_)

#### Login required:
_False_

### **[POST]** `/client/logout`

#### Parameters:
No

#### Login required:
_True_

### **[POST]** `/client/update`

#### Parameters:

* `first_name` (_not required, not blank_)
* `last_name` (_not required, not blank_)
* `description` (_not required, may be blank_)

#### Login required:
_True_

### **[POST]** `/client/friend/add`

#### Parameters:

* `user_id` (_required_)

#### Login required:
_True_

### **[POST]** `/client/friend/remove`

#### Parameters:

* `user_id` (_required_)

#### Login required:
_True_

## Channel API (`/api/channel`)

### **[POST]** `/get`

#### Parameters:

* `channel_id` (_required_)

#### Login required:
_True_

**Required channel permission**: `watch_channel_information_permission`

### **[POST]** `/update`

#### Parameters:

* `channel_id` (_required_)
* `title` (_not required_)
* `description` (_not required_)

#### Login required:
_True_

**Required channel permission**: `edit_channel_permission`

### **[POST]** `/create`

#### Parameters:

* `title` (_required_)
* `description` (_not required, default=""_)
* `companions` (_not required, default=[]_)

#### Login required:
_True_

**Required channel permission**: `edit_channel_permission`

### **[POST]** `/member/get`

#### Parameters:

* `channel_id` (_required_)
* `user_id` (_required_)

#### Login required:
_True_

**Required channel permission**: `watch_channel_members_permission`

### **[POST]** `/member/fetch`

#### Parameters:

* `channel_id` (_required_)
* `permissions` (_not required_) - list of permissions, which fetched users must have
* `page` (_not required, >= 0, default=0_)
* `page_results` (_not required, 0, <= 50, default=20_)

#### Login required:
_True_

**Required channel permission**: `watch_channel_members_permission`

### **[POST]** `/message/fetch`

#### Parameters:

* `channel_id` (_required_)
* `page` (_not required, >= 0, default=0_)
* `page_results` (_not required, 0, <= 50, default=20_)

#### Login required:
_True_

**Required channel permission**: `read_channel_permission`

### **[POST]** `/message/send`

#### Parameters:

* `channel_id` (_required_)
* `text` (_required, not blank_)

#### Login required:
_True_

**Required channel permission**: `send_messages_permission`

## Invitation API (`/api/invitation`)

### **[POST]** `/delete`

#### Parameters:

* `invitation_id` (_required_)

#### Login required:
_True_

### **[POST]** `/use`

#### Parameters:

* `invitation_id` (_required_)

#### Login required:
_True_
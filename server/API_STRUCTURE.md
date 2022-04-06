# Структура API 

## User API (`/api/user`)

### **GET** `/get_client_user`

> **Parameters**: Нет
> 
> **Login required**: _True_

### **GET** `/get_user`

> **Parameters**:
> * `user_id` (_required_)
> 
> **Login required**: _False_

### **POST** `/update_profile`

> **Parameters**:
> * `first_name` (_not required, not blank_)
> * `last_name` (_not required, not blank_)
> * `description` (_not required, may be blank_)
> 
> **Login required**: _True_

### **POST** add_friend

> **Parameters**:
> * `user_id` (_required_)
> 
> **Login required**: _True_

### **POST** `/remove_friend`

> **Parameters**:
> * `user_id` (_required_)
> 
> **Login required**: _True_

## Channel API (`/api/channel`)

### **GET** `/get_channel`

> **Parameters**:
> * `channel_id` (_required_)
> 
> **Login required**: _True_
> 
> **Required channel permission**: `watch_channel_information_permission`

### **POST** `/update_channel`

> **Parameters**:
> * `channel_id` (_required_)
> * `title` (_not required_)
> * `description` (_not required_)
> 
> **Login required**: _True_
> 
> **Required channel permission**: `edit_channel_permission`

### **POST** `/delete_invitation`

> **Parameters**:
> * `invitation_id` (_required_)
> 
> **Login required**: _True_

### **POST** `/use_invitation`

> **Parameters**:
> * `invitation_id` (_required_)
> 
> **Login required**: _True_



### **GET** `/get_member`

> **Parameters**:
> * `channel_id` (_required_)
> * `user_id` (_required_)
> 
> **Login required**: _True_
> 
> **Required channel permission**: `watch_channel_members_permission`

### **GET** `/fetch_members`

> **Parameters**:
> * `channel_id` (_required_)
> * `permissions` (_not required_) - list of permissions, which fetched users must have
> * `page` (_not required, >= 0, default=0_)
> * `page_results` (_not required, > 0, <= 50, default=20_)
> 
> **Login required**: _True_
> 
> **Required channel permission**: `watch_channel_members_permission`

### **GET** `/fetch_messages`

> **Parameters**:
> * `channel_id` (_required_)
> * `page` (_not required, >= 0, default=0_)
> * `page_results` (_not required, > 0, <= 50, default=20_)
> 
> **Login required**: _True_
> 
> **Required channel permission**: `read_channel_permission`

### **GET** `/send_message`

> **Parameters**:
> * `channel_id` (_required_)
> * `text` (_required, not blank_)
> 
> **Login required**: _True_
> 
> **Required channel permission**: `send_messages_permission`

## api/generate_key post

### in
+ username    string
+ userpassword    string

### out
+ msg    string
+ user_key    string

---

## api/connect_db post
### in
+ key    string

### out
+ msg    string

---

## api/search_userkey post
### in
+ username    string
+ userpassword    string

### out
+ msg    string
+ key    string

---

## api/push_data post
### in
+ key    string  
+ data    string
+ index_key    string

### out
+ msg    string
+ blockid    string
+ blockheight    string

---

## api/block_height post
### in
+ blockid    string  [if it's empty , return the chain height]

### out
+ msg    string
+ blockheight    string

---

## api/get_data post
### in
+ blockid    string  

### out
+ msg    string
+ data    string

---

## api/search_data post
### in
+ keywords    string  

### out
+ msg    string
+ datalist    list

---

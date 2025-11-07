# ADMIN CBS

ADMIN_MAIN = "adm:menu"
ACCESS_MENU = "adm:access"
ROLES_MENU = "adm:roles"


REQ_GRANT = "adm:req:grant"
REQ_ADMIN = "adm:req:admin"
REQ_CUR = "adm:req:curator"


ACCESS_LIST_PREFIX = "adm:access:list"  # + :{page}
ACCESS_TOGGLE_PREFIX = "adm:access:toggle"  # + :{tg_id}:{have}

ROLES_LIST_PREFIX = "adm:roles:list"  # + :{page}
ROLES_CHANGE_PREFIX = "adm:roles:change"  # + :{tg_id}
ROLES_SET_PREFIX = "adm:roles:set"  # + :{tg_id}:{role}

PROFILES_LIST_PREFIX = "adm:profiles"

USER_PROFILE_PREFIX = "adm:user:profile"  # + :{tg_id}
# CURATOR CBS

CURATOR_MENU = "cur:menu"

CUR_LIST_PREFIX = "cur:list"  # + :{page}
CUR_OPEN_PREFIX = "cur:open"  # + :{resp_id}
CUR_OK_PREFIX = "cur:ok"  # + :{resp_id}
CUR_REJECT_PREFIX = "cur:reject"  # + :{resp_id}

CUR_LIST_FINAL_PREFIX = "cur:final"   # + :{page}
CUR_OPEN_FINAL_PREFIX = "cur:open_final"   # + :{attempt_id}
CUR_COMMENT_FINAL_PREFIX = "cur:final_comment"   # + :{attempt_id}

# USER CBS

USER_OPEN_DOB = "dob_open"
USER_ED_FULL_NAME = "edit:full_name"
USER_ED_PHONE = "edit:phone"
USER_ED_SEX = "edit:sex"
USER_ED_DOB = "edit:dob"
USER_ED_BACK = "edit:back"

USER_SEX_MAN = "sex:man"
USER_SEX_WOMAN = "sex:woman"

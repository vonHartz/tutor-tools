SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

CREDIT_DIR := credits
SUBMISSIONS_DIR := submissions
UTILS_DIR := utils
OTHER_DIRS := private public
CONF_DIR := .conf
TASK_DIR = Tasks
NAME_SCRIPT := get_names.py
FEEDBACK_SCRIPT := feedback.py
CREATE_CREDITS_SCRIPT := create_credits.py
PARSE_CREDITS_SCRIPT := parse_credits.py
POST_JSON_SCRIPT := post_json.py
CREDITS_JSON_PREFIX := credits
EXERCISE_FOLDER_PREFIX := uebungsblatt-
TUTANTS_CONF_FILE := tuts.txt
FEEDBACK_FILE := feedback-tutor.txt
TASK_CONF_PREFIX := task
COURSE_URL := https://daphne.informatik.uni-freiburg.de/ss2020/AlgoDat/
SVN_URL = $(COURSE_URL)svn/
BULK_URL = $(COURSE_URL)solutions/bulk/
SVN_USER := XXX
SIGNATURE = '\nBei Fragen zur Korrektur (Punktabzüge usw.) bin ich jederzeit per Mail erreichbar.\n\n XXX <xxx@xxx.xx>'


PW ?= $(shell stty -echo; read -p "Password: " pwd; stty echo; echo $$pwd)

checkout = $(info $(shell svn checkout --username $(SVN_USER) $(SVN_URL)$(1) $(2)))

checkout-or-update = $(if $(shell [[ -d $(2) ]] && echo y),$(call update-folder,$(2)),$(call checkout,$(1),$(2)))

clean_up_and_push = $(info $(shell cd $(SUBMISSIONS_DIR)/$(1) ; make -C $(EXERCISE_FOLDER_PREFIX)$(2) clean ; svn commit -m "Feedback hinzugefügt"))

update-folder =  $(info $(shell svn update --username $(SVN_USER) $(1) && echo Updated $(1)))

.PHONY: test
test: load-tut-list
	@echo $(TUT_LIST)

.PHONY: load-tut-list
load-tut-list: $(CONF_DIR)/$(TUTANTS_CONF_FILE)
	$(eval TUT_LIST := $(shell cat $(CONF_DIR)/$(TUTANTS_CONF_FILE)))

.PHONY: checkout-all
checkout-all: load-tut-list $(SUBMISSIONS_DIR)
	@$(foreach tut, $(TUT_LIST), $(call checkout,$(tut)))

.PHONY: checkout-or-update-all
checkout-or-update-all: load-tut-list $(SUBMISSIONS_DIR)
	@$(foreach dir, $(OTHER_DIRS), $(call checkout-or-update,$(dir),$(dir)))
	@$(foreach tut, $(TUT_LIST), $(call checkout-or-update,$(tut),$(SUBMISSIONS_DIR)/$(tut)))


aggr%: @$(CREDIT_DIR)/$(CREDITS_JSON_PREFIX)-$(EXERCISE_FOLDER_PREFIX)%.json ;

feedback%: FORCE
	$(UTILS_DIR)/$(FEEDBACK_SCRIPT) $(FEEDBACK_FILE) $(EXERCISE_FOLDER_PREFIX) $* $(TASK_DIR)/tasks$*.json $(SUBMISSIONS_DIR) $(SVN_USER) $(SIGNATURE) --add

post_credits%: $(CREDIT_DIR)/$(CREDITS_JSON_PREFIX)-$(EXERCISE_FOLDER_PREFIX)%.json FORCE
	$(UTILS_DIR)/$(POST_JSON_SCRIPT) $(BULK_URL) $(CREDIT_DIR)/$(CREDITS_JSON_PREFIX)-$(EXERCISE_FOLDER_PREFIX)$*.json $(SVN_USER) $(PW)

push%: load-tut-list FORCE
	@$(foreach tut, $(TUT_LIST), $(call clean_up_and_push,$(tut),$*))

upload%: push% post_credits% FORCE;

$(CONF_DIR):
	@mkdir -p $(CONF_DIR)

$(CREDIT_DIR):
	@mkdir -p $(CREDIT_DIR)

$(SUBMISSIONS_DIR):
	@mkdir -p $(SUBMISSIONS_DIR)

$(CONF_DIR)/$(TUTANTS_CONF_FILE): $(CONF_DIR) FORCE
	@$(UTILS_DIR)/$(NAME_SCRIPT) $(COURSE_URL) $(SVN_USER) $(PW) > $(CONF_DIR)/$(TUTANTS_CONF_FILE)

$(CREDIT_DIR)/$(CREDITS_JSON_PREFIX)-$(EXERCISE_FOLDER_PREFIX)%.json: $(CREDIT_DIR)
	@$(UTILS_DIR)/$(CREATE_CREDITS_SCRIPT) $* $(SVN_USER) $(SUBMISSIONS_DIR) $(CREDIT_DIR) $(CREDITS_JSON_PREFIX) $(UTILS_DIR)/$(PARSE_CREDITS_SCRIPT)

.PHONY: clean
clean: clean-conf clean-credits clean-others clean-submissions

.PHONY: clean-conf
clean-conf:
	rm -r --interactive=never $(CONF_DIR)

.PHONY: clean-credits
clean-credits:
	rm -r --interactive=never $(CREDIT_DIR)

.PHONY: clean-others
clean-others:
	rm -r --interactive=never $(OTHER_DIRS)

.PHONY: clean-submissions
clean-submissions:
	rm -r --interactive=never $(SUBMISSIONS_DIR)

FORCE:

# -*- coding:utf-8 -*-
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
)

from modules.models.models import get_model
from modules.train_func import *
from modules.repo import *
from modules.webui import *
from modules.overwrites import patch_gradio
from modules.presets import *
from modules.utils import *
from modules.config import *
from modules import config
import gradio as gr
import colorama

logging.getLogger("httpx").setLevel(logging.WARNING)

patch_gradio()

# with open("web_assets/css/ChuanhuChat.css", "r", encoding="utf-8") as f:
#     ChuanhuChatCSS = f.read()


def create_new_model():
    return get_model(model_name=MODELS[DEFAULT_MODEL], access_key=my_api_key)[0]


with gr.Blocks(theme=small_and_beautiful_theme) as demo:
    user_name = gr.Textbox("", visible=False)
    promptTemplates = gr.State(load_template(get_template_names()[0], mode=2))
    user_question = gr.State("")
    assert type(my_api_key) == str
    user_api_key = gr.State(my_api_key)
    current_model = gr.State()
    topic = gr.State(i18n("Unnamed Dialog History"))

    with gr.Row(elem_id="chuanhu-header"):
        gr.HTML(get_html("header_title.html").format(
            app_title=CHUANHU_TITLE), elem_id="app-title")
        status_display = gr.Markdown(get_geoip, elem_id="status-display")
    with gr.Row(elem_id="float-display"):
        user_info = gr.Markdown(
            value="getting user info...", elem_id="user-info")
        update_info = gr.HTML(get_html("update.html").format(
            current_version=repo_tag_html(),
            version_time=version_time(),
            cancel_btn=i18n("Cancel"),
            update_btn=i18n("Update"),
            seenew_btn=i18n("Details"),
            ok_btn=i18n("OK"),
            close_btn=i18n("Close"),
            reboot_btn=i18n("Restart now"),
        ), visible=check_update)

    with gr.Row(equal_height=True, elem_id="chuanhu-body"):

        with gr.Column(elem_id="menu-area"):
            with gr.Column(elem_id="chuanhu-history"):
                with gr.Group():
                    with gr.Row(elem_id="chuanhu-history-header"):
                        with gr.Row(elem_id="chuanhu-history-search-row"):
                            with gr.Column(min_width=150, scale=2):
                                historySearchTextbox = gr.Textbox(show_label=False, container=False, placeholder=i18n(
                                    "Search (regex supported)..."), lines=1, elem_id="history-search-tb")
                            with gr.Column(min_width=52, scale=1, elem_id="gr-history-header-btns"):
                                uploadHistoryBtn = gr.UploadButton(
                                    interactive=True, label="", file_types=[".json"], elem_id="gr-history-upload-btn", type="binary")
                                historyRefreshBtn = gr.Button("", elem_id="gr-history-refresh-btn")


                    with gr.Row(elem_id="chuanhu-history-body"):
                        with gr.Column(scale=6, elem_id="history-select-wrap"):
                            historySelectList = gr.Radio(
                                label=i18n("Load conversation from list"),
                                choices=get_history_names(),
                                value=get_first_history_name(),
                                # multiselect=False,
                                container=False,
                                elem_id="history-select-dropdown"
                            )
                        with gr.Row(visible=False):
                            with gr.Column(min_width=42, scale=1):
                                historyDeleteBtn = gr.Button(
                                    "🗑️", elem_id="gr-history-delete-btn")
                    with gr.Row(visible=False):
                        with gr.Column(scale=6):
                            saveFileName = gr.Textbox(
                                show_label=True,
                                placeholder=i18n("Set file name: default .json, optional .md"),
                                label=i18n("Set save file name"),
                                value=i18n("Conversation history"),
                                elem_classes="no-container"
                                # container=False,
                            )
                        with gr.Column(scale=1):
                            renameHistoryBtn = gr.Button(
                                i18n("💾 Save conversation"), elem_id="gr-history-save-btn")
                            downloadHistoryJSONBtn = gr.DownloadButton(
                                i18n("History (JSON)"), elem_id="gr-history-download-json-btn")
                            downloadHistoryMarkdownBtn = gr.DownloadButton(
                                i18n("Export as Markdown"), elem_id="gr-history-download-md-btn")

            with gr.Column(elem_id="chuanhu-menu-footer"):
                with gr.Row(elem_id="chuanhu-func-nav"):
                    gr.HTML(get_html("func_nav.html"))
                # gr.HTML(get_html("footer.html").format(versions=versions_html()), elem_id="footer")
                # gr.Markdown(CHUANHU_DESCRIPTION, elem_id="chuanhu-author")

        with gr.Column(elem_id="chuanhu-area", scale=5):
            with gr.Column(elem_id="chatbot-area"):
                with gr.Row(elem_id="chatbot-header"):
                    model_select_dropdown = gr.Dropdown(
                        label=i18n("Select model"), choices=MODELS, multiselect=False, value=MODELS[DEFAULT_MODEL], interactive=True,
                        show_label=False, container=False, elem_id="model-select-dropdown", filterable=False
                    )
                    lora_select_dropdown = gr.Dropdown(
                        label=i18n("Select model"), choices=[], multiselect=False, interactive=True, visible=False,
                        container=False,
                    )
                    gr.HTML(get_html("chatbot_header_btn.html").format(
                        json_label=i18n("History (JSON)"),
                        md_label=i18n("Export as Markdown")
                    ), elem_id="chatbot-header-btn-bar")
                with gr.Row():
                    chatbot = gr.Chatbot(
                        label="Chuanhu Chat",
                        elem_id="chuanhu-chatbot",
                        latex_delimiters=latex_delimiters_set,
                        sanitize_html=False,
                        # height=700,
                        show_label=False,
                        avatar_images=[config.user_avatar, config.bot_avatar],
                        show_share_button=False,
                        placeholder=setPlaceholder(model_name=MODELS[DEFAULT_MODEL]),
                    )
                with gr.Row(elem_id="chatbot-footer"):
                    with gr.Column(elem_id="chatbot-input-box"):
                        with gr.Row(elem_id="chatbot-input-row"):
                            gr.HTML(get_html("chatbot_more.html").format(
                                single_turn_label=i18n("Single-turn conversation"),
                                websearch_label=i18n("Web search"),
                                upload_file_label=i18n("Upload file"),
                                uploaded_files_label=i18n("Knowledge base files"),
                                uploaded_files_tip=i18n("Manage knowledge base files in toolbox")
                            ))
                            with gr.Row(elem_id="chatbot-input-tb-row"):
                                with gr.Column(min_width=225, scale=12):
                                    user_input = gr.Textbox(
                                        elem_id="user-input-tb",
                                        show_label=False,
                                        placeholder=i18n("Type here"),
                                        elem_classes="no-container",
                                        max_lines=5,
                                        # container=False
                                    )
                                with gr.Column(min_width=42, scale=1, elem_id="chatbot-ctrl-btns"):
                                    submitBtn = gr.Button(
                                        value="", variant="primary", elem_id="submit-btn")
                                    cancelBtn = gr.Button(
                                        value="", variant="secondary", visible=False, elem_id="cancel-btn")
                        # Note: Buttons below are set invisible in UI. But they are used in JS.
                        with gr.Row(elem_id="chatbot-buttons", visible=False):
                            with gr.Column(min_width=120, scale=1):
                                emptyBtn = gr.Button(
                                    i18n("🧹 New conversation"), elem_id="empty-btn"
                                )
                            with gr.Column(min_width=120, scale=1):
                                retryBtn = gr.Button(
                                    i18n("🔄 Regenerate"), elem_id="gr-retry-btn")
                            with gr.Column(min_width=120, scale=1):
                                delFirstBtn = gr.Button(i18n("🗑️ Delete oldest conversation"))
                            with gr.Column(min_width=120, scale=1):
                                delLastBtn = gr.Button(
                                    i18n("🗑️ Delete latest conversation"), elem_id="gr-dellast-btn")
                            with gr.Row(visible=False) as like_dislike_area:
                                with gr.Column(min_width=20, scale=1):
                                    likeBtn = gr.Button(
                                        "👍", elem_id="gr-like-btn")
                                with gr.Column(min_width=20, scale=1):
                                    dislikeBtn = gr.Button(
                                        "👎", elem_id="gr-dislike-btn")

        with gr.Column(elem_id="toolbox-area", scale=1):
            # For CSS setting, there is an extra box. Don't remove it.
            with gr.Group(elem_id="chuanhu-toolbox"):
                with gr.Row():
                    gr.Markdown("## "+i18n("Toolbox"))
                    gr.HTML(get_html("close_btn.html").format(
                        obj="toolbox"), elem_classes="close-btn")
                with gr.Tabs(elem_id="chuanhu-toolbox-tabs"):
                    with gr.Tab(label=i18n("Conversation")):
                        with gr.Accordion(label=i18n("Model"), open=not HIDE_MY_KEY, visible=not HIDE_MY_KEY):
                            modelDescription = gr.Markdown(
                                elem_id="gr-model-description",
                                value=i18n(MODEL_METADATA[MODELS[DEFAULT_MODEL]]["description"]),
                                visible=False,
                            )
                            keyTxt = gr.Textbox(
                                show_label=True,
                                placeholder=f"Your API-key...",
                                value=hide_middle_chars(user_api_key.value),
                                type="password",
                                visible=not HIDE_MY_KEY,
                                label="API-Key",
                                elem_id="api-key"
                            )
                            if multi_api_key:
                                usageTxt = gr.Markdown(i18n(
                                    "Multi-account mode enabled; start chatting without key"), elem_id="usage-display", elem_classes="insert-block", visible=show_api_billing)
                            else:
                                usageTxt = gr.Markdown(i18n(
                                    "**Send a message** or **submit a key** to show quota"), elem_id="usage-display", elem_classes="insert-block", visible=show_api_billing)
                        gr.Markdown("---", elem_classes="hr-line", visible=not HIDE_MY_KEY)
                        with gr.Accordion(label="Prompt", open=True):
                            systemPromptTxt = gr.Textbox(
                                show_label=True,
                                placeholder=i18n("Enter system prompt here..."),
                                label="System prompt",
                                value=INITIAL_SYSTEM_PROMPT,
                                lines=8
                            )
                            retain_system_prompt_checkbox = gr.Checkbox(
                                label=i18n("Keep prompt when starting new conversation"), value=False, visible=True, elem_classes="switch-checkbox")
                            with gr.Accordion(label=i18n("Load prompt template"), open=False):
                                with gr.Column():
                                    with gr.Row():
                                        with gr.Column(scale=6):
                                            templateFileSelectDropdown = gr.Dropdown(
                                                label=i18n("Select prompt template set file"),
                                                choices=get_template_names(),
                                                multiselect=False,
                                                value=get_template_names()[0],
                                                # container=False,
                                            )
                                        with gr.Column(scale=1):
                                            templateRefreshBtn = gr.Button(
                                                i18n("🔄 Refresh"))
                                    with gr.Row():
                                        with gr.Column():
                                            templateSelectDropdown = gr.Dropdown(
                                                label=i18n("Load from prompt templates"),
                                                choices=load_template(
                                                    get_template_names()[
                                                        0], mode=1
                                                ),
                                                multiselect=False,
                                                # container=False,
                                            )
                        gr.Markdown("---", elem_classes="hr-line")
                        with gr.Accordion(label=i18n("Knowledge base"), open=True, elem_id="gr-kb-accordion"):
                            use_websearch_checkbox = gr.Checkbox(label=i18n(
                                "Use online search"), value=False, elem_classes="switch-checkbox", elem_id="gr-websearch-cb", visible=False)
                            index_files = gr.Files(label=i18n(
                                "Upload"), type="filepath", file_types=[".pdf", ".docx", ".pptx", ".epub", ".xlsx", ".txt", "text", "image"], elem_id="upload-index-file")
                            two_column = gr.Checkbox(label=i18n(
                                "Two-column PDF"), value=advance_docs["pdf"].get("two_column", False))
                            summarize_btn = gr.Button(i18n("Summarize"))
                            # TODO: formula OCR
                            # formula_ocr = gr.Checkbox(label=i18n("Recognize formulas"), value=advance_docs["pdf"].get("formula_ocr", False))

                    with gr.Tab(label=i18n("Parameters")):
                        gr.Markdown(i18n("# ⚠️ Change with caution ⚠️"),
                                    elem_id="advanced-warning")
                        with gr.Accordion(i18n("Parameters"), open=True):
                            temperature_slider = gr.Slider(
                                minimum=-0,
                                maximum=2.0,
                                value=1.0,
                                step=0.1,
                                interactive=True,
                                label="temperature",
                            )
                            top_p_slider = gr.Slider(
                                minimum=-0,
                                maximum=1.0,
                                value=1.0,
                                step=0.05,
                                interactive=True,
                                label="top-p",
                            )
                            n_choices_slider = gr.Slider(
                                minimum=1,
                                maximum=10,
                                value=1,
                                step=1,
                                interactive=True,
                                label="n choices",
                            )
                            stop_sequence_txt = gr.Textbox(
                                show_label=True,
                                placeholder=i18n("Stop sequences, separated by commas..."),
                                label="stop",
                                value="",
                                lines=1,
                            )
                            max_context_length_slider = gr.Slider(
                                minimum=1,
                                maximum=32768,
                                value=2000,
                                step=1,
                                interactive=True,
                                label="max context",
                            )
                            max_generation_slider = gr.Slider(
                                minimum=1,
                                maximum=32768,
                                value=1000,
                                step=1,
                                interactive=True,
                                label="max generations",
                            )
                            presence_penalty_slider = gr.Slider(
                                minimum=-2.0,
                                maximum=2.0,
                                value=0.0,
                                step=0.01,
                                interactive=True,
                                label="presence penalty",
                            )
                            frequency_penalty_slider = gr.Slider(
                                minimum=-2.0,
                                maximum=2.0,
                                value=0.0,
                                step=0.01,
                                interactive=True,
                                label="frequency penalty",
                            )
                            logit_bias_txt = gr.Textbox(
                                show_label=True,
                                placeholder=f"word:likelihood",
                                label="logit bias",
                                value="",
                                lines=1,
                            )
                            user_identifier_txt = gr.Textbox(
                                show_label=True,
                                placeholder=i18n("Used to locate abuse behavior"),
                                label=i18n("User identifier"),
                                value=user_name.value,
                                lines=1,
                            )
                    with gr.Tab(label=i18n("Extensions")):
                        gr.Markdown(
                            "Will be here soon...\n(We hope)\n\nAnd we hope you can help us to make more extensions!")

                    # changeAPIURLBtn = gr.Button(i18n("🔄 Switch API URL"))

    with gr.Row(elem_id="popup-wrapper"):
        with gr.Group(elem_id="chuanhu-popup"):
            with gr.Group(elem_id="chuanhu-setting"):
                with gr.Row():
                    gr.Markdown("## "+i18n("Settings"))
                    gr.HTML(get_html("close_btn.html").format(
                        obj="box"), elem_classes="close-btn")
                with gr.Tabs(elem_id="chuanhu-setting-tabs"):
                    # with gr.Tab(label=i18n("Model")):
                        # model_select_dropdown = gr.Dropdown(
                        #     label=i18n("Select model"), choices=MODELS, multiselect=False, value=MODELS[DEFAULT_MODEL], interactive=True
                        # )
                        # lora_select_dropdown = gr.Dropdown(
                        #     label=i18n("Select LoRA model"), choices=[], multiselect=False, interactive=True, visible=False
                        # )
                        # with gr.Row():


                    with gr.Tab(label=i18n("Advanced")):
                        gr.HTML(get_html("appearance_switcher.html").format(
                            label=i18n("Toggle light/dark theme")), elem_classes="insert-block", visible=False)
                        use_streaming_checkbox = gr.Checkbox(
                            label=i18n("Stream responses"), value=True, visible=ENABLE_STREAMING_OPTION, elem_classes="switch-checkbox no-container"
                        )
                        language_select_dropdown = gr.Dropdown(
                            label=i18n("Select reply language (for search & indexing)"),
                            choices=REPLY_LANGUAGES,
                            multiselect=False,
                            value=REPLY_LANGUAGES[0],
                            elem_classes="no-container",
                        )
                        name_chat_method = gr.Dropdown(
                            label=i18n("Conversation naming method"),
                            choices=HISTORY_NAME_METHODS,
                            multiselect=False,
                            interactive=True,
                            value=HISTORY_NAME_METHODS[chat_name_method_index],
                            elem_classes="no-container",
                        )
                        single_turn_checkbox = gr.Checkbox(label=i18n(
                            "Single-turn conversation"), value=False, elem_classes="switch-checkbox", elem_id="gr-single-session-cb", visible=False)
                        # checkUpdateBtn = gr.Button(i18n("🔄 Check for updates..."), visible=check_update)

                        logout_btn = gr.Button("Logout", link="/logout")

                    with gr.Tab(i18n("Network")):
                        gr.Markdown(
                            i18n("⚠️ To keep API key safe, modify network settings in `config.json`"), elem_id="netsetting-warning")
                        default_btn = gr.Button(i18n("🔙 Restore default network settings"))
                        # Network proxy
                        proxyTxt = gr.Textbox(
                            show_label=True,
                            placeholder=i18n("No proxy set..."),
                            label=i18n("Proxy address"),
                            value=config.http_proxy,
                            lines=1,
                            interactive=False,
                            # container=False,
                            elem_classes="view-only-textbox no-container",
                        )
                        # changeProxyBtn = gr.Button(i18n("🔄 Set proxy address"))
                        # Show custom api_host first
                        apihostTxt = gr.Textbox(
                            show_label=True,
                            placeholder="api.openai.com",
                            label="OpenAI API-Host",
                            value=config.api_host or shared.API_HOST,
                            lines=1,
                            interactive=False,
                            # container=False,
                            elem_classes="view-only-textbox no-container",
                        )

                    with gr.Tab(label=i18n("About"), elem_id="about-tab"):
                        gr.Markdown(
                            '<img alt="Chuanhu Chat logo" src="file=web_assets/icon/any-icon-512.png" style="max-width: 144px;">')
                        gr.Markdown("# "+i18n("Chuanhu Chat"))
                        gr.HTML(get_html("footer.html").format(
                            versions=versions_html()), elem_id="footer")
                        gr.Markdown(CHUANHU_DESCRIPTION, elem_id="description")

            with gr.Group(elem_id="chuanhu-training"):
                with gr.Row():
                    gr.Markdown("## "+i18n("Training"))
                    gr.HTML(get_html("close_btn.html").format(
                        obj="box"), elem_classes="close-btn")
                with gr.Tabs(elem_id="chuanhu-training-tabs"):
                    with gr.Tab(label="OpenAI "+i18n("Fine-tuning")):
                        openai_train_status = gr.Markdown(label=i18n("Training status"), value=i18n(
                            "See [usage tutorial](https://github.com/GaiZhenbiao/ChuanhuChatGPT/wiki/%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B#%E5%BE%AE%E8%B0%83-gpt-35)"))

                        with gr.Tab(label=i18n("Prepare dataset")):
                            dataset_previewjson = gr.JSON(
                                label=i18n("Dataset preview"))
                            dataset_selection = gr.Files(label=i18n("Select dataset"), file_types=[
                                                         ".xlsx", ".jsonl"], file_count="single")
                            upload_to_openai_btn = gr.Button(
                                i18n("Upload to OpenAI"), variant="primary", interactive=False)

                        with gr.Tab(label=i18n("Training")):
                            openai_ft_file_id = gr.Textbox(label=i18n(
                                "File ID"), value="", lines=1, placeholder=i18n("Automatically filled after uploading to OpenAI"))
                            openai_ft_suffix = gr.Textbox(label=i18n(
                                "Model name suffix"), value="", lines=1, placeholder=i18n("Optional, used to distinguish different models"))
                            openai_train_epoch_slider = gr.Slider(label=i18n(
                                "Training epochs"), minimum=1, maximum=100, value=3, step=1, interactive=True)
                            openai_start_train_btn = gr.Button(
                                i18n("Start training"), variant="primary", interactive=False)

                        with gr.Tab(label=i18n("Status")):
                            openai_status_refresh_btn = gr.Button(i18n("Refresh status"))
                            openai_cancel_all_jobs_btn = gr.Button(
                                i18n("Cancel all tasks"))
                            add_to_models_btn = gr.Button(
                                i18n("Add trained model to model list"), interactive=False)

            with gr.Group(elem_id="web-config", visible=False):
                gr.HTML(get_html('web_config.html').format(
                    enableCheckUpdate_config=check_update,
                    hideHistoryWhenNotLoggedIn_config=hide_history_when_not_logged_in,
                    forView_i18n=i18n("View only"),
                    deleteConfirm_i18n_pref=i18n("Are you sure you want to delete "),
                    deleteConfirm_i18n_suff=i18n("?"),
                    usingLatest_i18n=i18n("You are using the latest version!"),
                    updatingMsg_i18n=i18n("Attempting to update..."),
                    updateSuccess_i18n=i18n("Update successful, please restart this program"),
                    updateFailure_i18n=i18n(
                        "Update failed, please try [manual update](https://github.com/GaiZhenbiao/ChuanhuChatGPT/wiki/%E4%BD%BF%E7%94%A8%E6%95%99%E7%A8%8B#%E6%89%8B%E5%8A%A8%E6%9B%B4%E6%96%B0)"),
                    regenerate_i18n=i18n("Regenerate"),
                    deleteRound_i18n=i18n("Delete this round"),
                    renameChat_i18n=i18n("Rename this conversation"),
                    validFileName_i18n=i18n("Please enter a valid file name without the following special characters:"),
                    clearFileHistoryMsg_i18n=i18n("⚠️ Please delete historical files in the knowledge base before uploading!"),
                    dropUploadMsg_i18n=i18n("Drop files to upload"),
                ))
            with gr.Group(elem_id="fake-gradio-components", visible=False):
                updateChuanhuBtn = gr.Button(
                    visible=False, elem_classes="invisible-btn", elem_id="update-chuanhu-btn")
                rebootChuanhuBtn = gr.Button(
                    visible=False, elem_classes="invisible-btn", elem_id="reboot-chuanhu-btn")
                changeSingleSessionBtn = gr.Button(
                    visible=False, elem_classes="invisible-btn", elem_id="change-single-session-btn")
                changeOnlineSearchBtn = gr.Button(
                    visible=False, elem_classes="invisible-btn", elem_id="change-online-search-btn")
                historySelectBtn = gr.Button(
                    visible=False, elem_classes="invisible-btn", elem_id="history-select-btn")  # Not used

    # https://github.com/gradio-app/gradio/pull/3296

    def create_greeting(request: gr.Request):
        if hasattr(request, "username") and request.username:  # is not None or is not ""
            logging.info(f"Get User Name: {request.username}")
            user_info, user_name = gr.Markdown(
                value=f"User: {request.username}"), request.username
        else:
            user_info, user_name = gr.Markdown(
                value=f"", visible=False), ""
        current_model = get_model(
            model_name=MODELS[DEFAULT_MODEL], access_key=my_api_key, user_name=user_name)[0]
        if not hide_history_when_not_logged_in or user_name:
            loaded_stuff = current_model.auto_load()
        else:
            current_model.new_auto_history_filename()
            loaded_stuff = [gr.update(), gr.update(), gr.Chatbot(label=MODELS[DEFAULT_MODEL]), current_model.single_turn, current_model.temperature, current_model.top_p, current_model.n_choices, current_model.stop_sequence, current_model.token_upper_limit, current_model.max_generation_token, current_model.presence_penalty, current_model.frequency_penalty, current_model.logit_bias, current_model.user_identifier, gr.DownloadButton(), gr.DownloadButton()]
        return user_info, user_name, current_model, toggle_like_btn_visibility(DEFAULT_MODEL), *loaded_stuff, init_history_list(user_name, prepend=current_model.history_file_path.rstrip(".json"))
    demo.load(create_greeting, inputs=None, outputs=[
              user_info, user_name, current_model, like_dislike_area, saveFileName, systemPromptTxt, chatbot, single_turn_checkbox, temperature_slider, top_p_slider, n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider, presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt, use_streaming_checkbox, downloadHistoryJSONBtn, downloadHistoryMarkdownBtn, historySelectList], api_name="load")
    chatgpt_predict_args = dict(
        fn=predict,
        inputs=[
            current_model,
            user_question,
            chatbot,
            use_websearch_checkbox,
            index_files,
            language_select_dropdown,
        ],
        outputs=[chatbot, status_display],
        show_progress=True,
        concurrency_limit=CONCURRENT_COUNT
    )

    start_outputing_args = dict(
        fn=start_outputing,
        inputs=[],
        outputs=[submitBtn, cancelBtn],
        show_progress=True,
    )

    end_outputing_args = dict(
        fn=end_outputing, inputs=[], outputs=[submitBtn, cancelBtn]
    )

    reset_textbox_args = dict(
        fn=reset_textbox, inputs=[], outputs=[user_input]
    )

    transfer_input_args = dict(
        fn=transfer_input, inputs=[user_input], outputs=[
            user_question, user_input, submitBtn, cancelBtn], show_progress=True
    )

    get_usage_args = dict(
        fn=billing_info, inputs=[current_model], outputs=[
            usageTxt], show_progress=False
    )

    load_history_from_file_args = dict(
        fn=load_chat_history,
        inputs=[current_model, historySelectList],
        outputs=[saveFileName, systemPromptTxt, chatbot, single_turn_checkbox, temperature_slider, top_p_slider, n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider, presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt, use_streaming_checkbox, downloadHistoryJSONBtn, downloadHistoryMarkdownBtn],
    )

    refresh_history_args = dict(
        fn=get_history_list, inputs=[user_name], outputs=[historySelectList]
    )

    auto_name_chat_history_args = dict(
        fn=auto_name_chat_history,
        inputs=[current_model, name_chat_method, user_question, single_turn_checkbox],
        outputs=[historySelectList],
        show_progress=False,
    )

    # Chatbot
    cancelBtn.click(interrupt, [current_model], [])

    user_input.submit(**transfer_input_args).then(**
                                                  chatgpt_predict_args).then(**end_outputing_args).then(**auto_name_chat_history_args)
    user_input.submit(**get_usage_args)

    # user_input.submit(auto_name_chat_history, [current_model, user_question, chatbot, user_name], [historySelectList], show_progress=False)

    submitBtn.click(**transfer_input_args).then(**chatgpt_predict_args,
                                                api_name="predict").then(**end_outputing_args).then(**auto_name_chat_history_args)
    submitBtn.click(**get_usage_args)

    # submitBtn.click(auto_name_chat_history, [current_model, user_question, chatbot, user_name], [historySelectList], show_progress=False)

    index_files.upload(handle_file_upload, [current_model, index_files, chatbot, language_select_dropdown], [
                       index_files, chatbot, status_display])
    summarize_btn.click(handle_summarize_index, [
                        current_model, index_files, chatbot, language_select_dropdown], [chatbot, status_display])

    emptyBtn.click(
        reset,
        inputs=[current_model, retain_system_prompt_checkbox],
        outputs=[chatbot, status_display, historySelectList, systemPromptTxt, single_turn_checkbox, temperature_slider, top_p_slider, n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider, presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt, use_streaming_checkbox],
        show_progress=True,
        js='(a,b)=>{return clearChatbot(a,b);}',
    )

    retryBtn.click(**start_outputing_args).then(
        retry,
        [
            current_model,
            chatbot,
            use_websearch_checkbox,
            index_files,
            language_select_dropdown,
        ],
        [chatbot, status_display],
        show_progress=True,
    ).then(**end_outputing_args)
    retryBtn.click(**get_usage_args)

    delFirstBtn.click(
        delete_first_conversation,
        [current_model],
        [status_display],
    )

    delLastBtn.click(
        delete_last_conversation,
        [current_model, chatbot],
        [chatbot, status_display],
        show_progress=False
    )

    likeBtn.click(
        like,
        [current_model],
        [status_display],
        show_progress=False
    )

    dislikeBtn.click(
        dislike,
        [current_model],
        [status_display],
        show_progress=False
    )

    two_column.change(update_doc_config, [two_column], None)

    # LLM Models
    keyTxt.change(set_key, [current_model, keyTxt], [
                  user_api_key, status_display], api_name="set_key").then(**get_usage_args)
    keyTxt.submit(**get_usage_args)
    single_turn_checkbox.change(
        set_single_turn, [current_model, single_turn_checkbox], None, show_progress=False)
    use_streaming_checkbox.change(set_streaming, [current_model, use_streaming_checkbox], None, show_progress=False)
    model_select_dropdown.change(get_model, [model_select_dropdown, lora_select_dropdown, user_api_key, temperature_slider, top_p_slider, systemPromptTxt, user_name, current_model], [
                                 current_model, status_display, chatbot, lora_select_dropdown, user_api_key, keyTxt, modelDescription, use_streaming_checkbox], show_progress=True, api_name="get_model")
    model_select_dropdown.change(toggle_like_btn_visibility, [model_select_dropdown], [
                                 like_dislike_area], show_progress=False)
    # model_select_dropdown.change(
    #     toggle_file_type, [model_select_dropdown], [index_files], show_progress=False)
    lora_select_dropdown.change(get_model, [model_select_dropdown, lora_select_dropdown, user_api_key, temperature_slider,
                                top_p_slider, systemPromptTxt, user_name, current_model], [current_model, status_display, chatbot, modelDescription], show_progress=True)

    # Template
    systemPromptTxt.change(set_system_prompt, [
                           current_model, systemPromptTxt], None)
    templateRefreshBtn.click(get_template_dropdown, None, [
                             templateFileSelectDropdown])
    templateFileSelectDropdown.input(
        load_template,
        [templateFileSelectDropdown],
        [promptTemplates, templateSelectDropdown],
        show_progress=True,
    )
    templateSelectDropdown.change(
        get_template_content,
        [promptTemplates, templateSelectDropdown, systemPromptTxt],
        [systemPromptTxt],
        show_progress=True,
    )

    # S&L
    renameHistoryBtn.click(
        rename_chat_history,
        [current_model, saveFileName],
        [historySelectList],
        show_progress=True,
        js='(a,b,c,d)=>{return saveChatHistory(a,b,c,d);}'
    )
    historyRefreshBtn.click(**refresh_history_args)
    historyDeleteBtn.click(delete_chat_history, [current_model, historySelectList], [status_display, historySelectList, chatbot], js='(a,b,c)=>{return showConfirmationDialog(a, b, c);}').then(
        reset,
        inputs=[current_model, retain_system_prompt_checkbox],
        outputs=[chatbot, status_display, historySelectList, systemPromptTxt],
        show_progress=True,
        js='(a,b)=>{return clearChatbot(a,b);}',
    )
    historySelectList.select(**load_history_from_file_args)
    uploadHistoryBtn.upload(upload_chat_history, [current_model, uploadHistoryBtn], [
                        saveFileName, systemPromptTxt, chatbot, single_turn_checkbox, temperature_slider, top_p_slider, n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider, presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt, use_streaming_checkbox, downloadHistoryJSONBtn, downloadHistoryMarkdownBtn, historySelectList]).then(**refresh_history_args)
    historySearchTextbox.input(
        filter_history,
        [user_name, historySearchTextbox],
        [historySelectList]
    )

    # Train
    dataset_selection.upload(handle_dataset_selection, dataset_selection, [
                             dataset_previewjson, upload_to_openai_btn, openai_train_status])
    dataset_selection.clear(handle_dataset_clear, [], [
                            dataset_previewjson, upload_to_openai_btn])
    upload_to_openai_btn.click(upload_to_openai, [dataset_selection], [
                               openai_ft_file_id, openai_train_status], show_progress=True)

    openai_ft_file_id.change(lambda x: gr.update(interactive=True) if len(
        x) > 0 else gr.update(interactive=False), [openai_ft_file_id], [openai_start_train_btn])
    openai_start_train_btn.click(start_training, [
                                 openai_ft_file_id, openai_ft_suffix, openai_train_epoch_slider], [openai_train_status])

    openai_status_refresh_btn.click(get_training_status, [], [
                                    openai_train_status, add_to_models_btn])
    add_to_models_btn.click(add_to_models, [], [
                            model_select_dropdown, openai_train_status], show_progress=True)
    openai_cancel_all_jobs_btn.click(
        cancel_all_jobs, [], [openai_train_status], show_progress=True)

    # Advanced
    temperature_slider.input(
        set_temperature, [current_model, temperature_slider], None, show_progress=False)
    top_p_slider.input(set_top_p, [current_model, top_p_slider], None, show_progress=False)
    n_choices_slider.input(
        set_n_choices, [current_model, n_choices_slider], None, show_progress=False)
    stop_sequence_txt.input(
        set_stop_sequence, [current_model, stop_sequence_txt], None, show_progress=False)
    max_context_length_slider.input(
        set_token_upper_limit, [current_model, max_context_length_slider], None, show_progress=False)
    max_generation_slider.input(
        set_max_tokens, [current_model, max_generation_slider], None, show_progress=False)
    presence_penalty_slider.input(
        set_presence_penalty, [current_model, presence_penalty_slider], None, show_progress=False)
    frequency_penalty_slider.input(
        set_frequency_penalty, [current_model, frequency_penalty_slider], None, show_progress=False)
    logit_bias_txt.input(
        set_logit_bias, [current_model, logit_bias_txt], None, show_progress=False)
    user_identifier_txt.input(set_user_identifier, [
                               current_model, user_identifier_txt], None, show_progress=False)

    default_btn.click(
        reset_default, [], [apihostTxt, proxyTxt, status_display], show_progress=True
    )
    # changeAPIURLBtn.click(
    #     change_api_host,
    #     [apihostTxt],
    #     [status_display],
    #     show_progress=True,
    # )
    # changeProxyBtn.click(
    #     change_proxy,
    #     [proxyTxt],
    #     [status_display],
    #     show_progress=True,
    # )
    # checkUpdateBtn.click(fn=None, js='manualCheckUpdate')

    # Invisible elements
    updateChuanhuBtn.click(
        update_chuanhu,
        [user_name],
        [status_display],
        show_progress=True,
    )
    rebootChuanhuBtn.click(
        reboot_chuanhu,
        [],
        [],
        show_progress=True,
        js='rebootingChuanhu'
    )
    changeSingleSessionBtn.click(
        fn=lambda value: gr.Checkbox(value=value),
        inputs=[single_turn_checkbox],
        outputs=[single_turn_checkbox],
        js='(a)=>{return bgChangeSingleSession(a);}'
    )
    changeOnlineSearchBtn.click(
        fn=lambda value: gr.Checkbox(value=value),
        inputs=[use_websearch_checkbox],
        outputs=[use_websearch_checkbox],
        js='(a)=>{return bgChangeOnlineSearch(a);}'
    )
    historySelectBtn.click(  # This is an experimental feature... Not actually used.
        fn=load_chat_history,
        inputs=[current_model, historySelectList],
        outputs=[saveFileName, systemPromptTxt, chatbot, single_turn_checkbox, temperature_slider, top_p_slider, n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider, presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt, use_streaming_checkbox, downloadHistoryJSONBtn, downloadHistoryMarkdownBtn],
        js='(a,b)=>{return bgSelectHistory(a,b);}'
    )

# Start local server by default, accessible via IP, no public share link by default
demo.title = i18n("Chuanhu Chat 🚀")

if __name__ == "__main__":
    reload_javascript()
    setup_wizard()
    demo.queue().launch(
        allowed_paths=["web_assets"],
        blocked_paths=["config.json", "files", "models", "lora", "modules", "history"],
        server_name=server_name,
        server_port=server_port,
        share=share,
        auth=auth_from_conf if authflag else None,
        favicon_path="./web_assets/favicon.ico",
        inbrowser=autobrowser and not dockerflag,  # Disable inbrowser when running in Docker
    )

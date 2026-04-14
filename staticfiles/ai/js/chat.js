const query = (obj) =>
  Object.keys(obj)
    .map((k) => encodeURIComponent(k) + "=" + encodeURIComponent(obj[k]))
    .join("&");
const colorThemes = document.querySelectorAll('[name="theme"]');
const markdown = window.markdownit();
const message_box = document.getElementById(`messages`);
const message_input = document.getElementById(`message-input`);
const box_conversations = document.querySelector(`.top`);
const spinner = box_conversations.querySelector(".spinner");
const stop_generating = document.querySelector(`.stop_generating`);
const chatForm = document.querySelector(`#chat-form`);
let nothingToLoad = document.querySelector(`#nothing-to-load`)
let suggesitonBox = document.querySelector("#suggestion-box")
let prompt_lock = false;
let keep_generating = true;
const suggestions = [
  [0, "Create a workout plan", "for resistance training", "I need to start resistance training. Can you create a 7-day workout plan for me to ease into it?"],
  [1, "Give me ideas", "about how to plan New Years resolution", "Give me 3 ideas about how to plan good New Years resolutions. Give me some that are personal, family, and professionally-oriented."],
  [2, "Write a thank-you note", "to my interviewer", "Write 2-3 sentences to thank my interviewer, reiterating my excitement for the job opportunity while keeping it cool. Don't make it too formal."],
  [3, "Create a content calendar", "for a TikTok account", "Create a content calendar for a TikTok account on reviewing real estate listings."],
  [4, "Help me pick", "an outfit that will look good on camera", "I have a photoshoot tomorrow. Can you recommend me some colors and outfit options that will look good on camera?"],
  [5, "Design a database schema", "for an online merch store", "Design a database schema for an online merch store."],
  [6, "Tell me a fun fact", "about the Roman Empire", "Tell me a random fun fact about the Roman Empire"],
  [7, "Write a Python script" ,"to automate sending daily email reports", "Write a script to automate sending daily email reports in Python, and walk me through how I would set it up."],
  [8, "Plan a trip" ,"to see the northern lights in Norway", "Plan a 3-day trip to see the northern lights in Norway. Also recommend any ideal dates."],
]

hljs.addPlugin(new CopyButtonPlugin());


const format = (text) => {
  return text.replace(/(?:\r\n|\r|\n)/g, "<br>");
};

message_input.addEventListener("blur", () => {
  // window.scrollTo(0, 0);
});

message_input.addEventListener("focus", () => {
  // document.documentElement.scrollTop = document.documentElement.scrollHeight;
});

const delete_conversations = async () => {
  localStorage.clear();
  await new_conversation();
};

const handle_ask = async () => {
  // message_input.style.height = `80px`;
  message_input.focus();

  // window.scrollTo(0, 0);
  let message = message_input.value;
  if (message.length > 0) {
    message_input.value = ``;
    nothingToLoad = document.querySelector(`#nothing-to-load`)
    if(nothingToLoad)nothingToLoad.style.display = "none";
    console.log(window.conversation_id)
    document.getElementById('new_convo').setAttribute('disabled', '')
    Array.from(document.querySelectorAll('.convo')).map(ele=>ele.style['pointer-events']='none')
    await ask_gpt(message);
    Array.from(document.querySelectorAll('.convo')).map(ele=>ele.style['pointer-events']='unset')
    document.getElementById('new_convo').removeAttribute('disabled')
  }
};

const remove_cancel_button = async () => {
  stop_generating.classList.add(`stop_generating-hiding`);

  setTimeout(() => {
    stop_generating.classList.remove(`stop_generating-hiding`);
    stop_generating.classList.add(`stop_generating-hidden`);
  }, 300);
};

const ask_gpt = async (message) => {
  const _conversation_id = window.conversation_id
  //  = window.token
  // try {
    message_input.value = ``;
    message_input.innerHTML = ``;
    message_input.innerText = ``;

    add_conversation(window.conversation_id, message.substr(0, 20));
    // window.scrollTo(0, 0);
    window.controller = new AbortController();

    // jailbreak = document.getElementById("jailbreak");
    // model = document.getElementById("model");
    prompt_lock = true;
    window.text = ``;
    const _token = message_id();

    stop_generating.classList.remove(`stop_generating-hidden`);

    message_box.innerHTML += `
            <div class="message">
                <div class="user">
                    ${user_image}
                </div>
                <div class="content" id="user_${_token}"> 
                    ${format(message)}
                </div>
            </div>
        `;

    /* .replace(/(?:\r\n|\r|\n)/g, '<br>') */

    message_box.scrollTop = message_box.scrollHeight;
    // window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 500));
    // window.scrollTo(0, 0);

    message_box.innerHTML += `
            <div class="message">
                <div class="user">
                    ${gpt_image}
                </div>
                <div class="content" id="gpt_${_token}">
                    <div id="cursor"></div>
                </div>
            </div>
        `;

    message_box.scrollTop = message_box.scrollHeight;
    // window.scrollTo(0, 0);
    await new Promise((r) => setTimeout(r, 1000));
    // window.scrollTo(0, 0);
    console.log("sending post request")
    const response = await fetch(`/conversation/`, {
      method: `POST`,
      signal: window.controller.signal,
      headers: {
        "content-type": `application/json`,
          accept: `text/event-stream`,
          'X-CSRFToken': chatForm.querySelector('input').getAttribute("value")
      },
      body: JSON.stringify({
        conversation_id: _conversation_id,
        action: `_ask`,
        // jailbreak: jailbreak.options[jailbreak.selectedIndex].value,
        meta: {
          id: _token,
          content: {
            conversation: await get_conversation(_conversation_id),
            conversation_id: _conversation_id,
            content_type: "text",
            parts: [
              {
                content: message,
                role: "user",
              },
            ],
          },
        },
      }),
    });
    let status = response.status
    const reader = response.body.getReader();
    let counter = 0;
    keep_generating=true
    stop_generating.addEventListener("click", ()=>{keep_generating=false})
    while (true) {
      if(!keep_generating)break
      if (counter==10)break
      counter+=1
      const { value, done } = await reader.read();
      if (done) break;
      
      chunk = new TextDecoder().decode(value);
      await new Promise(resolve => setTimeout(resolve, 200));
      // chunk = "message "

      // if (
      //   chunk.includes(
      //     `<form id="challenge-form" action="/backend-api/v2/conversation?`
      //   )
      // ) {
      //   chunk = `cloudflare token expired, please refresh the page.`;
      // }

      if(status>300){
        text = `an Error has occured please; status code ${status}`
      }else{
        text += chunk;
      }

      // const objects         = chunk.match(/({.+?})/g);

      // try { if (JSON.parse(objects[0]).success === false) throw new Error(JSON.parse(objects[0]).error) } catch (e) {}

      // objects.forEach((object) => {
      //     console.log(object)
      //     try { text += h2a(JSON.parse(object).content) } catch(t) { console.log(t); throw new Error(t)}
      // });

      console.log(_token)
      document.getElementById(`gpt_${_token}`).innerHTML =
        markdown.render(text);
      document.querySelectorAll(`code`).forEach((el) => {
        hljs.highlightElement(el);
      });

      // window.scrollTo(0, 0);
      message_box.scrollTo({ top: message_box.scrollHeight, behavior: "auto" });
    }

    // if text contains :
    if (
      text.includes(
        `instead. Maintaining this website and API costs a lot of money`
      )
    ) {
      document.getElementById(`gpt_${_token}`).innerHTML =
        "An error occured, please reload / refresh cache and try again.";
    }

    add_message(_conversation_id, "user", message);
    add_message(_conversation_id, "assistant", text);

    message_box.scrollTop = message_box.scrollHeight;
    await remove_cancel_button();
    prompt_lock = false;

    await load_conversations(20, 0);
    // window.scrollTo(0, 0);
  // } catch (e) {
  //   add_message(_conversation_id, "user", message);

  //   message_box.scrollTop = message_box.scrollHeight;
  //   await remove_cancel_button();
  //   prompt_lock = false;

  //   await load_conversations(20, 0);


  //   let cursorDiv = document.getElementById(`cursor`);
  //   if (cursorDiv) cursorDiv.parentNode.removeChild(cursorDiv);

  //   if (e.name != `AbortError`) {
  //     let error_message = `oops ! something went wrong, please try again / reload. [stacktrace in console]`;

  //     document.getElementById(`gpt_${_token}`).innerHTML = error_message;
  //     add_message(_conversation_id, "assistant", error_message);
  //   } else {
  //     document.getElementById(`gpt_${_token}`).innerHTML += ` [aborted]`;
  //     add_message(_conversation_id, "assistant", text + ` [aborted]`);
  //   }

  //   // window.scrollTo(0, 0);
  // }
};

const clear_conversations = async () => {
  const elements = box_conversations.childNodes;
  let index = elements.length;

  if (index > 0) {
    while (index--) {
      const element = elements[index];
      if (
        element.nodeType === Node.ELEMENT_NODE &&
        element.tagName.toLowerCase() !== `button`
      ) {
        box_conversations.removeChild(element);
      }
    }
  }
};

const clear_conversation = async () => {
  let messages = message_box.getElementsByTagName(`div`);

  while (messages.length > 0) {
    message_box.removeChild(messages[0]);
  }
};

const show_option = async (conversation_id) => {
  const conv = document.getElementById(`conv-${conversation_id}`);
  const yes = document.getElementById(`yes-${conversation_id}`);
  const not = document.getElementById(`not-${conversation_id}`);

  conv.style.display = "none";
  yes.style.display = "block";
  not.style.display = "block"; 
}

const hide_option = async (conversation_id) => {
  const conv = document.getElementById(`conv-${conversation_id}`);
  const yes = document.getElementById(`yes-${conversation_id}`);
  const not = document.getElementById(`not-${conversation_id}`);

  conv.style.display = "block";
  yes.style.display = "none";
  not.style.display = "none"; 
}

const delete_conversation = async (conversation_id) => {
  localStorage.removeItem(`conversation:${conversation_id}`);

  const conversation = document.getElementById(`convo-${conversation_id}`);
    conversation.remove();

  if (window.conversation_id == conversation_id) {
    await new_conversation();

  }

  await load_conversations(20, 0, true);
};

const set_conversation = async (conversation_id) => {
  history.pushState({}, null, `/chat/${conversation_id}`);
  window.conversation_id = conversation_id;

  await clear_conversation();
  await load_conversation(conversation_id);
  await load_conversations(20, 0, true);
};

const new_conversation = async () => {
  console.log('new conversation')
  window.conversation_id = uuid();
  history.pushState({}, null, `/chat/${conversation_id}`);
  
  await clear_conversation();
  await load_conversations(20, 0, true);
  nothingToLoad = document.createElement("div")
  message_box.appendChild(nothingToLoad)
  nothingToLoad.style.display = "flex";
  nothingToLoad.outerHTML = `<div class="messages-message-box" id="nothing-to-load"><div class="authentication-needed display-none"></div><div class="no-messages-to-display" id="no-messages-to-display"><div class="nomessages-gpt-icon"><svg width="41" height="41" viewBox="0 0 41 41" fill="none" xmlns="http://www.w3.org/2000/svg" class="h-2/3 w-2/3" role="img"><text x="-9999" y="-9999">ChatGPT</text><path d="M37.5324 16.8707C37.9808 15.5241 38.1363 14.0974 37.9886 12.6859C37.8409 11.2744 37.3934 9.91076 36.676 8.68622C35.6126 6.83404 33.9882 5.3676 32.0373 4.4985C30.0864 3.62941 27.9098 3.40259 25.8215 3.85078C24.8796 2.7893 23.7219 1.94125 22.4257 1.36341C21.1295 0.785575 19.7249 0.491269 18.3058 0.500197C16.1708 0.495044 14.0893 1.16803 12.3614 2.42214C10.6335 3.67624 9.34853 5.44666 8.6917 7.47815C7.30085 7.76286 5.98686 8.3414 4.8377 9.17505C3.68854 10.0087 2.73073 11.0782 2.02839 12.312C0.956464 14.1591 0.498905 16.2988 0.721698 18.4228C0.944492 20.5467 1.83612 22.5449 3.268 24.1293C2.81966 25.4759 2.66413 26.9026 2.81182 28.3141C2.95951 29.7256 3.40701 31.0892 4.12437 32.3138C5.18791 34.1659 6.8123 35.6322 8.76321 36.5013C10.7141 37.3704 12.8907 37.5973 14.9789 37.1492C15.9208 38.2107 17.0786 39.0587 18.3747 39.6366C19.6709 40.2144 21.0755 40.5087 22.4946 40.4998C24.6307 40.5054 26.7133 39.8321 28.4418 38.5772C30.1704 37.3223 31.4556 35.5506 32.1119 33.5179C33.5027 33.2332 34.8167 32.6547 35.9659 31.821C37.115 30.9874 38.0728 29.9178 38.7752 28.684C39.8458 26.8371 40.3023 24.6979 40.0789 22.5748C39.8556 20.4517 38.9639 18.4544 37.5324 16.8707ZM22.4978 37.8849C20.7443 37.8874 19.0459 37.2733 17.6994 36.1501C17.7601 36.117 17.8666 36.0586 17.936 36.0161L25.9004 31.4156C26.1003 31.3019 26.2663 31.137 26.3813 30.9378C26.4964 30.7386 26.5563 30.5124 26.5549 30.2825V19.0542L29.9213 20.998C29.9389 21.0068 29.9541 21.0198 29.9656 21.0359C29.977 21.052 29.9842 21.0707 29.9867 21.0902V30.3889C29.9842 32.375 29.1946 34.2791 27.7909 35.6841C26.3872 37.0892 24.4838 37.8806 22.4978 37.8849ZM6.39227 31.0064C5.51397 29.4888 5.19742 27.7107 5.49804 25.9832C5.55718 26.0187 5.66048 26.0818 5.73461 26.1244L13.699 30.7248C13.8975 30.8408 14.1233 30.902 14.3532 30.902C14.583 30.902 14.8088 30.8408 15.0073 30.7248L24.731 25.1103V28.9979C24.7321 29.0177 24.7283 29.0376 24.7199 29.0556C24.7115 29.0736 24.6988 29.0893 24.6829 29.1012L16.6317 33.7497C14.9096 34.7416 12.8643 35.0097 10.9447 34.4954C9.02506 33.9811 7.38785 32.7263 6.39227 31.0064ZM4.29707 13.6194C5.17156 12.0998 6.55279 10.9364 8.19885 10.3327C8.19885 10.4013 8.19491 10.5228 8.19491 10.6071V19.808C8.19351 20.0378 8.25334 20.2638 8.36823 20.4629C8.48312 20.6619 8.64893 20.8267 8.84863 20.9404L18.5723 26.5542L15.206 28.4979C15.1894 28.5089 15.1703 28.5155 15.1505 28.5173C15.1307 28.5191 15.1107 28.516 15.0924 28.5082L7.04046 23.8557C5.32135 22.8601 4.06716 21.2235 3.55289 19.3046C3.03862 17.3858 3.30624 15.3413 4.29707 13.6194ZM31.955 20.0556L22.2312 14.4411L25.5976 12.4981C25.6142 12.4872 25.6333 12.4805 25.6531 12.4787C25.6729 12.4769 25.6928 12.4801 25.7111 12.4879L33.7631 17.1364C34.9967 17.849 36.0017 18.8982 36.6606 20.1613C37.3194 21.4244 37.6047 22.849 37.4832 24.2684C37.3617 25.6878 36.8382 27.0432 35.9743 28.1759C35.1103 29.3086 33.9415 30.1717 32.6047 30.6641C32.6047 30.5947 32.6047 30.4733 32.6047 30.3889V21.188C32.6066 20.9586 32.5474 20.7328 32.4332 20.5338C32.319 20.3348 32.154 20.1698 31.955 20.0556ZM35.3055 15.0128C35.2464 14.9765 35.1431 14.9142 35.069 14.8717L27.1045 10.2712C26.906 10.1554 26.6803 10.0943 26.4504 10.0943C26.2206 10.0943 25.9948 10.1554 25.7963 10.2712L16.0726 15.8858V11.9982C16.0715 11.9783 16.0753 11.9585 16.0837 11.9405C16.0921 11.9225 16.1048 11.9068 16.1207 11.8949L24.1719 7.25025C25.4053 6.53903 26.8158 6.19376 28.2383 6.25482C29.6608 6.31589 31.0364 6.78077 32.2044 7.59508C33.3723 8.40939 34.2842 9.53945 34.8334 10.8531C35.3826 12.1667 35.5464 13.6095 35.3055 15.0128ZM14.2424 21.9419L10.8752 19.9981C10.8576 19.9893 10.8423 19.9763 10.8309 19.9602C10.8195 19.9441 10.8122 19.9254 10.8098 19.9058V10.6071C10.8107 9.18295 11.2173 7.78848 11.9819 6.58696C12.7466 5.38544 13.8377 4.42659 15.1275 3.82264C16.4173 3.21869 17.8524 2.99464 19.2649 3.1767C20.6775 3.35876 22.0089 3.93941 23.1034 4.85067C23.0427 4.88379 22.937 4.94215 22.8668 4.98473L14.9024 9.58517C14.7025 9.69878 14.5366 9.86356 14.4215 10.0626C14.3065 10.2616 14.2466 10.4877 14.2479 10.7175L14.2424 21.9419ZM16.071 17.9991L20.4018 15.4978L24.7325 17.9975V22.9985L20.4018 25.4983L16.071 22.9985V17.9991Z" fill="currentColor"></path></svg></div><h2 class="nomessages-gpt-text">How can I help you today?</h2></div><div class="suggestion-box" id="suggestion-box"></div></div>`;
  suggesitonBox = document.querySelector("#suggestion-box")
  pickSugg(suggesitonBox);
};

const load_conversation = async (conversation_id) => {
  history.pushState({}, null, `/chat/${conversation_id}`);
  let conversation = await JSON.parse(
    localStorage.getItem(`conversation:${conversation_id}`)
  );
  // console.log(conversation, conversation_id);
  nothingToLoad = document.querySelector(`#nothing-to-load`)
  if(nothingToLoad)nothingToLoad.style.display = "none";
  if(!conversation || !conversation.items || conversation.items.length==0)return
  for (item of conversation.items) {
    message_box.innerHTML += `
            <div class="message">
                <div class="user">
                    ${item.role == "assistant" ? gpt_image : user_image}
                </div>
                <div class="content">
                    ${
                      item.role == "assistant"
                        ? markdown.render(item.content)
                        : item.content
                    }
                </div>
            </div>
        `;
  }

  document.querySelectorAll(`code`).forEach((el) => {
    hljs.highlightElement(el);
  });

  message_box.scrollTo({ top: message_box.scrollHeight, behavior: "smooth" });

  setTimeout(() => {
    message_box.scrollTop = message_box.scrollHeight;
  }, 500);
};

const get_conversation = async (conversation_id) => {
  let conversation = await JSON.parse(
    localStorage.getItem(`conversation:${conversation_id}`)
  );
  console.log("conversation", conversation.items)
  return conversation.items;
};

const add_conversation = async (conversation_id, title) => {
  if (localStorage.getItem(`conversation:${conversation_id}`) == null) {
    localStorage.setItem(
      `conversation:${conversation_id}`,
      JSON.stringify({
        id: conversation_id,
        title: title,
        items: [],
      })
    );
  }
};

const add_message = async (conversation_id, role, content) => {
  before_adding = JSON.parse(
    localStorage.getItem(`conversation:${conversation_id}`)
  );

  before_adding.items.push({
    role: role,
    content: content,
  });

  localStorage.setItem(
    `conversation:${conversation_id}`,
    JSON.stringify(before_adding)
  ); // update conversation
};

const load_conversations = async (limit, offset, loader) => {

  console.log("loading conversations");
  //if (loader === undefined) box_conversations.appendChild(spinner);

  let conversations = [];
  for (let i = 0; i < localStorage.length; i++) {
    if (localStorage.key(i).startsWith("conversation:")) {
      let conversation = localStorage.getItem(localStorage.key(i));
      conversations.push(JSON.parse(conversation));
    }
  }

  //if (loader === undefined) spinner.parentNode.removeChild(spinner)
  await clear_conversations();

  for (conversation of conversations) {
    box_conversations.innerHTML += `
    <div class="convo" id="convo-${conversation.id}">
      <div class="left" onclick="set_conversation('${conversation.id}')">
          <i class="fa-regular fa-comments"></i>
          <span class="convo-title">${conversation.title}</span>
      </div>
      <i onclick="show_option('${conversation.id}')" class="fa-regular fa-trash" id="conv-${conversation.id}"></i>
      <i onclick="delete_conversation('${conversation.id}')" class="fa-regular fa-check" id="yes-${conversation.id}" style="display:none;"></i>
      <i onclick="hide_option('${conversation.id}')" class="fa-regular fa-x" id="not-${conversation.id}" style="display:none;"></i>
    </div>
    `;
  }

  document.querySelectorAll(`code`).forEach((el) => {
    hljs.highlightElement(el);
  });
};

document.getElementById(`cancelButton`).addEventListener(`click`, async () => {
  window.controller.abort();
  console.log(`aborted ${window.conversation_id}`);
});

function h2a(str1) {
  var hex = str1.toString();
  var str = "";

  for (var n = 0; n < hex.length; n += 2) {
    str += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
  }

  return str;
}

const uuid = () => {
  return `xxxxxxxx-xxxx-4xxx-yxxx-${Date.now().toString(16)}`.replace(
    /[xy]/g,
    function (c) {
      var r = (Math.random() * 16) | 0,
        v = c == "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    }
  );
};

const message_id = () => {
  random_bytes = (Math.floor(Math.random() * 1338377565) + 2956589730).toString(
    2
  );
  unix = Math.floor(Date.now() / 1000).toString(2);

  return BigInt(`0b${unix}${random_bytes}`).toString();
};

window.onload = async () => {
  load_settings_localstorage();

  conversations = 0;
  for (let i = 0; i < localStorage.length; i++) {
    if (localStorage.key(i).startsWith("conversation:")) {
      conversations += 1;
    }
  }

  if (conversations == 0) localStorage.clear();

  await setTimeout(() => {
    load_conversations(20, 0);
  }, 1);

  if (!window.location.href.endsWith(`#`)) {
    if (/\/chat\/.+/.test(window.location.href)) {
      console.log('load_conversation')
      await load_conversation(window.conversation_id);
    }
  }
  clear_conversation()
  new_conversation()
message_input.addEventListener(`keydown`, async (evt) => {
    if (prompt_lock) return;
    if (evt.keyCode === 13 && !evt.shiftKey) {
        evt.preventDefault();
        await handle_ask();
    } else {
      message_input.style.removeProperty("height");
      // message_input.style.height = message_input.scrollHeight + 4 + "px";
    }
  });


register_settings_localstorage();
};
chatForm.addEventListener(`submit`, async e => {
  e.preventDefault();
  console.log("clicked send");
  if (prompt_lock) return;
  await handle_ask();
});

document.querySelector(".mobile-sidebar").addEventListener("click", (event) => {
  const sidebar = document.querySelector(".conversations");

  if (sidebar.classList.contains("shown")) {
    sidebar.classList.remove("shown");
    event.target.classList.remove("rotated");
  } else {
    sidebar.classList.add("shown");
    event.target.classList.add("rotated");
  }

  // window.scrollTo(0, 0);
});

const register_settings_localstorage = async () => {
  // settings_ids = ["switch", "model", "jailbreak"];
  settings_ids = [];
  settings_elements = settings_ids.map((id) => document.getElementById(id));
  settings_elements.map((element) =>
    element.addEventListener(`change`, async (event) => {
      switch (event.target.type) {
        case "checkbox":
          localStorage.setItem(event.target.id, event.target.checked);
          break;
        case "select-one":
          localStorage.setItem(event.target.id, event.target.selectedIndex);
          break;
        default:
          console.warn("Unresolved element type");
      }
    })
  );
};

const load_settings_localstorage = async () => {
  // settings_ids = ["switch", "model", "jailbreak"];
  settings_ids = [];
  settings_elements = settings_ids.map((id) => document.getElementById(id));
  settings_elements.map((element) => {
    if (localStorage.getItem(element.id)) {
      switch (element.type) {
        case "checkbox":
          element.checked = localStorage.getItem(element.id) === "true";
          break;
        case "select-one":
          element.selectedIndex = parseInt(localStorage.getItem(element.id));
          break;
        default:
          console.warn("Unresolved element type");
      }
    }
  });
};

// Theme storage for recurring viewers
// const storeTheme = function (theme) {
//   localStorage.setItem("theme", theme);
// };

// // set theme when visitor returns
// const setTheme = function () {
//   const activeTheme = localStorage.getItem("theme");
//   colorThemes.forEach((themeOption) => {
//     if (themeOption.id === activeTheme) {
//       themeOption.checked = true;
//     }
//   });
//   // fallback for no :has() support
//   document.documentElement.className = activeTheme;
// };

// colorThemes.forEach((themeOption) => {
//   themeOption.addEventListener("click", () => {
//     storeTheme(themeOption.id);
//     // fallback for no :has() support
//     document.documentElement.className = themeOption.id;
//   });
// });

// document.onload = setTheme();
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
function pickRandomItems(array, count) {
  const shuffledArray = shuffleArray(array.slice());
  return shuffledArray.slice(0, count);
}
function pickSugg(suggesitonBox){
  let sugg = pickRandomItems(suggestions, 4);
  sugg.map(s=>{
    let ele = document.createElement("div");
    suggesitonBox.appendChild(ele)
    ele.outerHTML = `<div class="suggestion-box-item pointer" id="suggested-${s[0]}">
    <h2>${s[1]}    
    <p>${s[2]}</p>
    </h2>
    <div class="gotoicon">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" class="icon-sm text-token-text-primary"><path d="M7 11L12 6L17 11M12 18V7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
    </div>
    </div>`
    document.getElementById(`suggested-${s[0]}`).addEventListener('click',(e) => {
      message_input.value = s[3];
      chatForm.querySelector('button').click()
    })
  })

}
pickSugg(suggesitonBox);
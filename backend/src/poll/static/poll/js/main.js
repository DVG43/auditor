document.addEventListener("DOMContentLoaded", () => {

  const headerAccordionText = document.querySelector('.header-accordion__text');
  const countBlock = document.querySelector('.header__count-block');
  const countText = document.querySelector('.header__count');
  const headerSelectBody = document.querySelector('.header-select__body');
  const answersLists = document.querySelectorAll('.question-answers-list');
  const navigateBtnNext = document.querySelector('.navigate__btn-next');
  const navigateBtnBack = document.querySelector('.navigate__btn-back');
  const pages = document.querySelectorAll('.page');
  let currentPage = 1;
  const pageAmount = pages.length;

  for (let i = 0; i < pageAmount; i++){
    const headerSelectItem = document.createElement('div');
    headerSelectItem.classList.add('header-select__item', 'select__item');
    headerSelectItem.innerHTML = `Страница ${i+1} из ${pageAmount}`;
    headerSelectItem.onclick = function() {
      changePage(i);
    };
    headerSelectBody.append(headerSelectItem);
  };

  accordionTextGenerator(5, 5, 5);
  select();
  accordion();

  navigateBtnNext.querySelector('.navigate__btn-info').innerHTML = `Страница ${currentPage+1}/${pageAmount}`;

  if (window.screen.availWidth >= 600){
    countBlock.classList.remove('passive');
    headerAccordionText.innerHTML = `Страница ${currentPage} из ${pageAmount}`;
  } else {
    countBlock.classList.add('passive');
  };

  const checkboxes = document.querySelectorAll('.checkbox-input');

  checkboxes.forEach((checkbox) => {
    checkbox.checked = localStorage.getItem(`${checkbox.name + checkbox.id}`);
    checkbox.addEventListener('click', () => {
      const questionContainer = checkbox.closest('.question-container');
      if(questionContainer.querySelector('.question__star-obligatory')){
        if (checkbox.checked){
          questionContainer.classList.remove('question-container-obligatory');
        } else {
          questionContainer.classList.add('question-container-obligatory');
        };
      };

      localStorage.setItem(`${checkbox.name + checkbox.id}`, checkbox.checked);
    });
  });

  const inputs = document.querySelectorAll('.question__input');

  inputs.forEach((input) => {
    input.addEventListener('input', () => {
      const questionContainer = input.closest('.question-container');
      if(questionContainer.querySelector('.question__star-obligatory')){
        if (input.value){
          questionContainer.classList.remove('question-container-obligatory');
        } else {
          questionContainer.classList.add('question-container-obligatory');
        };
      };
    });

    input.addEventListener('change', () => {
      localStorage.setItem(`${input.name + input.id}`, input.value);
    });

    input.value = localStorage.getItem(`${input.name + input.id}`);

  });  

  answersLists.forEach((answersList) => {
    const answersBtns = answersList.querySelectorAll('.question-answers-list__item-btn');

    answersBtns.forEach((answersBtn) => {
      answersBtn.addEventListener('click', (event) => {
        for(let i=0; i<answersBtns.length; i++){
          if(event.currentTarget === answersBtns[i]){
            answersBtns[i].classList.add('question-answers-list__item-btn-active');
          } else{
            answersBtns[i].classList.remove('question-answers-list__item-btn-active');
          };
        };
        accordionTextGenerator(5, 5, 5);
        const questionContainer = answersBtn.closest('.question-container-obligatory');
        if (questionContainer){
          questionContainer.classList.remove('question-container-obligatory');
        }
        
        localStorage.setItem(`${answersList.title + answersList.id}`, answersBtn.innerHTML);
      });

      if(localStorage.getItem(`${answersList.title + answersList.id}`) === answersBtn.innerHTML){
        answersBtn.classList.add('question-answers-list__item-btn-active');
      }
    });
  });

  const noteBtns = document.querySelectorAll('.question-action-list__item-note-btn');

  noteBtns.forEach((noteBtn) => {
    noteBtn.addEventListener('click', () => {
      const noteInput = document.createElement('input');

      noteInput.classList.add('question-note__input', 'input-resert');

      noteInput.type = 'text';
      noteInput.placeholder = 'Введите текст заметки...';

      noteBtn.closest('.question-action-list').before(noteInput);
    });
  });

  const fileInputs = document.querySelectorAll('.question-action-list__item-input');

  fileInputs.forEach((fileInput) => {
    fileInput.onchange = function () {
      let fileBox = this.closest('.question-container').querySelector('.question-file');
      if(!fileBox){
        fileBox = document.createElement('div');
        const fileTitle = document.createElement('h3');

        fileBox.classList.add('question-file');
        fileTitle.classList.add('question-file__title');
        fileTitle.innerHTML = 'Медиа';

        fileBox.append(fileTitle);
      }

      const fileBlock = document.createElement('div');

      if (this.value.includes('.png') || this.value.includes('.jpg') || this.value.includes('.svg')){
        fileBlock.classList.add('question-file__img-block');
        const fileImg = document.createElement('img');
        fileImg.classList.add('question-file__img');

        const file = this.files[0];
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function() {
          fileImg.src = reader.result;
        };
        reader.onerror = function() {
          console.log(reader.error);
        };

        fileBlock.append(fileImg);    
      } else{
        const fileText = document.createElement('p');
        fileBlock.classList.add('question-file__text-block');
        fileText.classList.add('question-file__text');
        fileText.innerHTML = this.files[0].name;
        fileBlock.append(fileText);
      };
    
      
      fileBox.append(fileBlock);
      this.closest('.question-action-list').before(fileBox);
    };
  });

  navigateBtnNext.addEventListener('click', () => {  
    flippNextPage(); 
  });

  navigateBtnBack.addEventListener('click', () => {
    flippBackPage();
  });

  const submitBtn = document.getElementById('submit-btn');
  const form = document.getElementById('form');

  submitBtn.addEventListener('click', () => {
    form.submit();
    const submitModal = document.createElement('div');
    const submitModalContainer = document.createElement('div');
    const submitSpiner = document.createElement('div');
    const submitSpinerText = document.createElement('span');
    const submitText = document.createElement('p');
    const submitAgainBtn = document.createElement('button');

    submitModal.classList.add('submit-modal', 'flex');
    submitModalContainer.classList.add('submit-modal-container', 'flex');
    submitSpiner.classList.add('submit-modal__spinner');
    submitSpinerText.classList.add('submit-modal__spinner-text');
    submitText.classList.add('submit-modal__text');
    submitAgainBtn.classList.add('submit-modal__btn', 'btn-resert');

    submitText.innerHTML = "Дождитесь окончания загрузки, чтобы не потерять Ваши данные";
    submitAgainBtn.innerHTML = 'Пройти еще раз';

    submitAgainBtn.onclick = () => {
      submitModal.remove();
    }

    submitSpiner.append(submitSpinerText);
    submitModalContainer.append(submitSpiner);
    submitModalContainer.append(submitText);
    submitModal.append(submitModalContainer);

    document.body.append(submitModal);

    setTimeout(() => {
      submitText.innerHTML = "Проверка завершена";
      submitText.classList.add('submit-modal__text-end');
      submitSpiner.remove();
      submitModalContainer.append(submitAgainBtn);
    }, 4000);

    console.log(form.elements);
  }) 

  window.addEventListener('resize', () => {
    accordionTextGenerator(5, 5, 5);
    if (window.screen.availWidth >= 600){
      countBlock.classList.remove('passive');
      headerAccordionText.innerHTML = 'Страница 1 из 2';
    } else {
      countBlock.classList.add('passive');
    };
  });

  const questionSelects = document.querySelectorAll('.question-select');

  questionSelects.forEach((questionSelect) => {
    const selectCheckboxes = questionSelect.querySelectorAll('.question-checkbox__input');
    const selectText = localStorage.getItem(`${questionSelect.title + questionSelect.id}`);

    if(selectText){
      questionSelect.querySelector('.select__current').innerHTML = selectText;
      for(let i=0; i<selectCheckboxes.length; i++){
        if(selectCheckboxes[i].nextElementSibling.innerHTML === selectText){
          selectCheckboxes[i].checked = true;
        };
      };
    };
  });

  function select() {
    const selectHeader = document.querySelectorAll('.select__header');
    const selectItem = document.querySelectorAll('.select__item');
    const selectBtn = document.querySelectorAll('.select__btn');
  
    selectHeader.forEach(item => {
      item.addEventListener('click', selectToggle);
    });
  
    selectItem.forEach(item => {
      item.addEventListener('click', selectChoose);
    });

    selectBtn.forEach(item => {
      item.addEventListener('click', selectClose);
    });
  
    function selectToggle() {
      this.parentElement.classList.toggle('is-active');
      this.querySelector('.select__icon').classList.toggle('rotate');
    };

    function selectClose() {
      const select = this.closest('.select');
      const selectCheckboxes = select.querySelectorAll('.question-checkbox__input');
      const selectIcon = this.closest('.select').querySelector('.select__icon');
      const currentText = select.querySelector('.select__current');
      let text;

      for(let i=0; i<selectCheckboxes.length; i++){
        if(selectCheckboxes[i].checked){
          text = selectCheckboxes[i].nextElementSibling.innerHTML;
        };
      };

      select.classList.remove('is-active');
      selectIcon.classList.remove('rotate');

      if(text){
        currentText.innerText = text;
        localStorage.setItem(`${select.title + select.id}`, text);

        const questionContainer = this.closest('.question-container-obligatory');
        if (questionContainer){
          questionContainer.classList.remove('question-container-obligatory');
        };
      };
      
    };
  
    function selectChoose() {
      const text = this.innerText;
      const select = this.closest('.select');
      const selectIcon = this.closest('.select').querySelector('.select__icon');
      const currentText = select.querySelector('.select__current');

      if(this.classList.contains('header-select__item')){
        if (window.screen.availWidth >= 600){
          currentText.innerText = text;
        } else{
          currentText.innerText = text + ' -' + currentText.innerHTML.split('-')[1];
        };
        select.classList.remove('is-active');
        selectIcon.classList.remove('rotate');
      } else{
        const selectCheckboxes = select.querySelectorAll('.question-checkbox__input');
        selectCheckboxes.forEach((selectCheckbox) => {
          selectCheckbox.addEventListener('click', (event) => {
            for(let i=0; i<selectCheckboxes.length; i++){
              if(event.currentTarget !== selectCheckboxes[i]){
                selectCheckboxes[i].checked = false;
              };
            };
          });
        });
      };
      
      //select.classList.remove('is-active');
      //selectIcon.classList.remove('rotate');

      
    }
  
  };

  function accordion() {
    const accordionHeader = document.querySelectorAll('.accordion__header');
  
    accordionHeader.forEach(item => {
      item.addEventListener('click', accordionToggle)
    });
  
    function accordionToggle() {
      this.parentElement.parentElement.classList.toggle('is-active');
      this.querySelector('.accordion__icon').classList.toggle('rotate');
    }
  
  };


  function accordionTextGenerator(yesPoints, noPoints, dnPoints){
    const voutedAnswers = document.querySelectorAll('.question-answers-list__item-btn-active');

    const points = Math.max(yesPoints, noPoints, dnPoints);
    const questionsPoints = answersLists.length * points;
    let count=0;

    for(let i=0; i<voutedAnswers.length; i++){
      if(voutedAnswers[i].classList.contains('yes-btn')){
        count+=yesPoints;
      } else if(voutedAnswers[i].classList.contains('no-btn')){
        count+=noPoints;
      } else if(voutedAnswers[i].classList.contains('dn-btn')){
        count+=dnPoints;
      } 
    }

    const percent = count*100/questionsPoints;

    if (window.screen.availWidth > 600){
      countText.innerHTML = `${count} / ${questionsPoints} (${percent}%)`;
    } else {
      headerAccordionText.innerHTML = `Страница ${currentPage} из ${pageAmount} - Оценка: ${count} из ${questionsPoints} (${percent}%)`;
    };
  };

  function flippNextPage() {   

    document.querySelector(`.page-${currentPage}`).classList.add('passive');
    navigateBtnBack.querySelector('.navigate__btn-info').innerHTML = `Страница ${currentPage}/${pageAmount}`;
    currentPage++;
    document.querySelector(`.page-${currentPage}`).classList.remove('passive');
    navigateBtnNext.querySelector('.navigate__btn-info').innerHTML = `Страница ${currentPage+1}/${pageAmount}`;


    if (currentPage === 2){
      navigateBtnBack.classList.remove('passive');
      navigateBtnNext.closest('.navigate-container').classList.remove('navigate-container-next');
    };

    if (currentPage === pageAmount){
      navigateBtnNext.classList.add('passive');
      navigateBtnNext.closest('.navigate-container').classList.add('navigate-container-back');
    };

    if (window.screen.availWidth >= 600){
      headerAccordionText.innerText = `Страница ${currentPage} из ${pageAmount}`;
    } else{
      headerAccordionText.innerText = `Страница ${currentPage} из ${pageAmount}` + ' -' + headerAccordionText.innerHTML.split('-')[1];
    };
  };

  function flippBackPage() {   

    document.querySelector(`.page-${currentPage}`).classList.add('passive');
    navigateBtnNext.querySelector('.navigate__btn-info').innerHTML = `Страница ${currentPage}/${pageAmount}`;
    currentPage--;
    document.querySelector(`.page-${currentPage}`).classList.remove('passive');
    navigateBtnBack.querySelector('.navigate__btn-info').innerHTML = `Страница ${currentPage-1}/${pageAmount}`;

    if (currentPage === 1){
      navigateBtnBack.classList.add('passive');
      navigateBtnNext.closest('.navigate-container').classList.add('navigate-container-next');
    };

    if (currentPage === pageAmount-1){
      navigateBtnNext.classList.remove('passive');
      navigateBtnNext.closest('.navigate-container').classList.remove('navigate-container-back');
    };

    if (window.screen.availWidth >= 600){
      headerAccordionText.innerText = `Страница ${currentPage} из ${pageAmount}`;
    } else{
      headerAccordionText.innerText = `Страница ${currentPage} из ${pageAmount}` + ' -' + headerAccordionText.innerHTML.split('-')[1];
    };
  };

  function changePage(i) {   
    navigateBtnBack.closest('.navigate-container').classList.remove('navigate-container-back');
    navigateBtnNext.closest('.navigate-container').classList.remove('navigate-container-next');
    navigateBtnBack.classList.remove('passive');
    navigateBtnNext.classList.remove('passive');

    document.querySelector(`.page-${currentPage}`).classList.add('passive');
    currentPage = i+1;
    document.querySelector(`.page-${currentPage}`).classList.remove('passive');

    navigateBtnBack.querySelector('.navigate__btn-info').innerHTML = `Страница ${currentPage-1}/${pageAmount}`; 
    navigateBtnNext.querySelector('.navigate__btn-info').innerHTML = `Страница ${currentPage+1}/${pageAmount}`;

    if (currentPage === 1){
      navigateBtnBack.classList.add('passive');
      navigateBtnBack.closest('.navigate-container').classList.add('navigate-container-next');
    };

    if (currentPage === pageAmount){
      navigateBtnNext.classList.add('passive');
      navigateBtnNext.closest('.navigate-container').classList.add('navigate-container-back');
    };
  }

})
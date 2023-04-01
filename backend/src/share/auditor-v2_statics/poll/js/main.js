document.addEventListener("DOMContentLoaded", () => {
  const headerAccordionText = document.querySelector('.header-accordion__text');
  const countBlock = document.querySelector('.header__count-block');
  const countText = document.querySelector('.header__count');
  const answersLists = document.querySelectorAll('.question-answers-list');

  accordionTextGenerator(5, 5, 5);
  select();
  accordion();

  if (window.screen.availWidth >= 600){
    countBlock.classList.remove('passive');
    headerAccordionText.innerHTML = 'Страница 1 из 2';
  } else {
    countBlock.classList.add('passive');
  };

  

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
      });
    });
  })

  

  const noteBtns = document.querySelectorAll('.question-action-list__item-note-btn');

  noteBtns.forEach((noteBtn) => {
    noteBtn.addEventListener('click', () => {
      const note = document.createElement('div');
      const noteText = document.createElement('span');
      const noteInput = document.createElement('input');

      note.classList.add('question-note', 'flex');
      noteText.classList.add('question-note__text');
      noteInput.classList.add('question-note__input', 'input-resert');

      noteInput.type = 'text';
      noteInput.placeholder = 'Введите текст заметки...';
      noteText.innerHTML = 'Текст заметки...';

      noteInput.oninput = () => {
        noteText.innerHTML = noteInput.value;
      };

      note.append(noteText);
      note.append(noteInput);

      noteBtn.closest('.question-action-list').classList.add('question-action-list-active');
      noteBtn.closest('.question-container').append(note);
    });
  });

  const fileInputs = document.querySelectorAll('#file-input');

  fileInputs.forEach((fileInput) => {
    fileInput.onchange = function () {
      console.log('Selected file: ' + this.value);

      const fileText = document.createElement('p');
      fileText.classList.add('question-file__text');
      fileText.innerHTML = 'Выбранный файл: ' + this.value;

      this.closest('.question-action-list').classList.add('question-action-list-active');
      this.closest('.question-container').append(fileText);
    };
  });

  const navigateBtnNext = document.querySelector('.navigate__btn-next');
  const navigateBtnBack = document.querySelector('.navigate__btn-back');

  navigateBtnNext.addEventListener('click', () => {
    navigateBtnNext.classList.add('passive');
    navigateBtnBack.classList.remove('passive');
    navigateBtnNext.closest('.navigate-container').classList.add('navigate-container-back');
    if (window.screen.availWidth >= 600){
      headerAccordionText.innerText = 'Страница 2 из 2';
    } else{
      headerAccordionText.innerText = 'Страница 2 из 2' + ' -' + headerAccordionText.innerHTML.split('-')[1];
    }
  });

  navigateBtnBack.addEventListener('click', () => {
    navigateBtnBack.classList.add('passive');
    navigateBtnNext.classList.remove('passive');
    navigateBtnNext.closest('.navigate-container').classList.remove('navigate-container-back');
    if (window.screen.availWidth >= 600){
      headerAccordionText.innerText = 'Страница 1 из 1';
    } else{
      headerAccordionText.innerText = 'Страница 1 из 2' + ' -' + headerAccordionText.innerHTML.split('-')[1];
    }
  });

  window.addEventListener('resize', () => {
    accordionTextGenerator(5, 5, 5);
    if (window.screen.availWidth >= 600){
      countBlock.classList.remove('passive');
      headerAccordionText.innerHTML = 'Страница 1 из 2';
    } else {
      countBlock.classList.add('passive');
    };
  });

  function select() {
    const selectHeader = document.querySelectorAll('.select__header');
    const selectItem = document.querySelectorAll('.select__item');
  
    selectHeader.forEach(item => {
      item.addEventListener('click', selectToggle)
    });
  
    selectItem.forEach(item => {
      item.addEventListener('click', selectChoose)
    });
  
    function selectToggle() {
      this.parentElement.classList.toggle('is-active');
      this.querySelector('.select__icon').classList.toggle('rotate');
    }
  
    function selectChoose() {
      const text = this.innerText;
      const select = this.closest('.select');
      const selectIcon = this.closest('.select').querySelector('.select__icon');
      const currentText = select.querySelector('.select__current');
      if (window.screen.availWidth >= 600){
        currentText.innerText = text;
      } else{
        currentText.innerText = text + ' -' + currentText.innerHTML.split('-')[1];
      }
      select.classList.remove('is-active');
      selectIcon.classList.remove('rotate');
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
        console.log(count);
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
      headerAccordionText.innerHTML = `Страница 1 из 2 - Оценка: ${count} из ${questionsPoints} (${percent}%)`;
    };
  };

})
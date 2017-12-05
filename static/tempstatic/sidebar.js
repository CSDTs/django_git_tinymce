document.addEventListener('DOMContentLoaded', function () {

  var docElem = document.documentElement;
  var sidebar = document.querySelector('.sidebar');
  // var board = sidebar.querySelector('.board');
  // var itemContainers = Array.prototype.slice.call(kanban.querySelectorAll('.board-column-content'));
  var itemContainers = sidebar.querySelector('.board-column-content');
  var columnGrids = [];
  var dragCounter = 0;
  var boardGrid;

    var muuri = new Muuri(itemContainers, {  
      items: '.board-item',
      layoutDuration: 400,
      layoutEasing: 'ease',
      dragEnabled: true,
      dragSortInterval: 0,
      // dragContainer: document.body,
      // dragContainer: sidebar,
      dragReleaseDuration: 400,
      dragReleaseEasing: 'ease'
    })
    .on('dragStart', function (item) {
      ++dragCounter;
      docElem.classList.add('dragging');
      item.getElement().style.width = item.getWidth() + 'px';
      item.getElement().style.height = item.getHeight() + 'px';
    })

    items = muuri.getItems();
    for (var i = 0; i < items.length; ++i){
      console.log(items[i].getElement().textContent);
    }
  });

// https://stackoverflow.com/questions/32435510/how-to-create-drag-drop-navigation-menu-manager-like-wordpress

// });

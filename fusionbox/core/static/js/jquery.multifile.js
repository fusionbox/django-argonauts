/**
 * jquery.multifile.js
 * by Rocky Meza
 *
 * Multifile is a plugin that provides a better interface for
 * uploading more than one file at a time.
 */
;(function($, global, undefined){
  $.fn.multifile = function(container, templateCb)
  {
    var $container
      , addInput = function(event)
        {
          var $this = $(this)
            , new_input = $this.clone(true, false);

          $this
            .unbind(event)
            .hide()
            .after(new_input);

          templateCb = templateCb || $.fn.multifile.templateCb;

          templateCb($.fn.multifile.getFileObject(this))
            .appendTo($container)
            .find('.multifile_remove_input')
              .bind('click.multifile', bindRemoveInput($this));
        }
      , bindRemoveInput = function($input)
        {
          // TODO: make this customizable
          return function(event)
          {
            $input.remove();
            $(this).parents('.uploaded_image').remove();

            event.preventDefault();
          };
        };

    if ( container )
    {
      if ( typeof container == 'string' )
        $container = $(container);
      else
        $container = container;
    }
    else
    {
      $container = $('<div class="multifile_container" />');
      this.after($container);
    }

    return this.each(function(index, elem)
    {
      $(this)
        .bind('change.multifile', addInput)
        ;
    });
  };

  $.fn.multifile.templateCb = function(file)
  {
    return $(
    '<p class="uploaded_image"> \
      <a href="" class="multifile_remove_input">x</a> \
    </p>')
      .append( $('<span>').attr('class', 'filename').text(file.name) );
  };

  $.fn.multifile.getFileObject = function(input)
  {
    var file = {};
    // check for HTML5 FileList support
    if ( !!global.FileList )
    {
      if ( input.files.length == 1 )
        file = input.files[0];
      else
      {
        file._multiple = true;

        // We do this in order to support `multiple` files.
        // You can't display them separately because they 
        // belong to only one file input.  It is impossible
        // to remove just one of the files.
        file.name = input.files[0].name;
        for (var i = 1, _len = input.files.length; i < _len; i++)
          file.name += ', ' + input.files[i].name;
      }
    }
    else
    {
      file._html4 = true;
      file.name = input.value;
    }

    return file;
  };
})(jQuery, this);

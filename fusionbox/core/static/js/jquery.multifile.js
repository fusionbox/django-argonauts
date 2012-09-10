;(function($, global, undefined)
{
  
  $.fn.multifile = function(container, template)
  {
    var $container = $(container)
      , $template  = $(template)
      , addInput   = function(event)
        {
          var $this = $(this)
            , new_input = $this.clone(true, false).val('');

          $this
            .unbind(event)
            .after(new_input);
        }
      , addInputAndRemover = function(event)
        {
          var $this = $(this);

          addInput.apply(this, arguments);

          $this.hide();

          for ( var i = 0, _len = this.files.length; i < _len; i++ )
          {
            $template
              .tmpl(this.files[i])
              .appendTo($container)
              .find('.remove_input')
                .bind('click.multifile', bindRemoveInput($this));
          }
        }
      , bindRemoveInput = function($input)
        {
          return function(event)
          {
            $input.remove();
            $(this).parents('.uploaded_image').remove();

            event.preventDefault();
          };
        };

    return this.each(function(index, elem)
    {
      // detect FileList support
      if ( !!global.FileList )
      {
        $(this)
          .bind('change.multifile', addInputAndRemover)
          ;
      }
      else
      {
        $(this)
          .bind('change.multifile', addInput)
          ;
        
        $container.hide();
      }
    });
  }
})(jQuery, this);

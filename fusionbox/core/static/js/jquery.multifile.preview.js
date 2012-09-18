;(function($, global, $multifile)
{
  if ( !global.FileReader )
    return;

  $multifile.templateCb = function(file)
  {
    var $tmpl = $('<p class="uploaded_image"> \
      <a href="" class="multifile_remove_input">x</a> \
      <span class="filename"></span> \
      <img class="multifile_preview" /> \
      <a class="multifile_preview"></a> \
    </p>')
      , fr = new FileReader();
    $tmpl.find('span.filename').text(file.name);
    fr.onload = $multifile.fileReaderCb($tmpl, file);
    fr.readAsDataURL(file);
    return $tmpl;
  };

  $multifile.image_filter = /^(?:image\/bmp|image\/cis\-cod|image\/gif|image\/ief|image\/jpeg|image\/jpeg|image\/jpeg|image\/pipeg|image\/png|image\/svg\+xml|image\/tiff|image\/x\-cmu\-raster|image\/x\-cmx|image\/x\-icon|image\/x\-portable\-anymap|image\/x\-portable\-bitmap|image\/x\-portable\-graymap|image\/x\-portable\-pixmap|image\/x\-rgb|image\/x\-xbitmap|image\/x\-xpixmap|image\/x\-xwindowdump)$/i;

  $multifile.fileReaderCb = function($tmpl, file_obj)
  {
    return function(event)
    {
      if ( $multifile.image_filter.test(file_obj.type) )
        $tmpl.find('img.multifile_preview')
          .attr('src', event.target.result);
      else
        $tmpl.find('a.multifile_preview')
          .attr('href', event.target.result)
          .text('Preview');
    };
  };

})(jQuery, this, $.fn.multifile);

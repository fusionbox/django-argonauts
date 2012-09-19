;(function($, global, multifile_plugin)
{
  var _parent_templateCb = multifile_plugin.templateCb;

  if ( !global.FileReader )
    return;

  multifile_plugin.templateCb = function(file)
  {
    return multifile_plugin.fileReaderCb(_parent_templateCb, file);
  };

  multifile_plugin.image_filter = /^(?:image\/bmp|image\/cis\-cod|image\/gif|image\/ief|image\/jpeg|image\/jpeg|image\/jpeg|image\/pipeg|image\/png|image\/svg\+xml|image\/tiff|image\/x\-cmu\-raster|image\/x\-cmx|image\/x\-icon|image\/x\-portable\-anymap|image\/x\-portable\-bitmap|image\/x\-portable\-graymap|image\/x\-portable\-pixmap|image\/x\-rgb|image\/x\-xbitmap|image\/x\-xpixmap|image\/x\-xwindowdump)$/i;

  multifile_plugin.fileReaderCb = function(templateCb, file)
  {
    var fr = new FileReader()
      , $tmpl = templateCb(file)
      , $img;
    fr.onload = function(event)
    {
      if ( multifile_plugin.image_filter.test(file.type) )
      {
        $img = $('<img />').attr({
          'class': 'multifile_preview',
          'src': event.target.result
          });
        $tmpl.append($img);
      }
    };
    fr.readAsDataURL(file);
    return $tmpl;
  };

})(jQuery, this, $.fn.multifile);

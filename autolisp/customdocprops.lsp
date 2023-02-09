(defun C:CUSTOMDOCPROPS (/ Info Num Index Custom)
  (vl-load-com)
  (setq acadObject (vlax-get-acad-object))
  (setq acadDocument (vla-get-ActiveDocument acadObject))

  ;;Get the SummaryInfo
  (setq Info (vlax-get-Property acadDocument 'SummaryInfo))
  (setq Num (vla-NumCustomInfo Info))
  (setq Index 0)
  (repeat Num
    (vla-getCustomByIndex Info Index 'ID 'Value)
    (setq Custom (cons (cons ID Value) Custom))
    (setq Index (1+ Index))
  )  ;repeat

  (if Custom (reverse Custom))
)

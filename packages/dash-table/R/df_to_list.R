df_to_list <- function(df) {
  if(!(is.data.frame(df)))
    stop("df_to_list requires a data.frame object; please verify that df is of the correct type.")
  setNames(lapply(split(df, seq(nrow(df))), 
                  FUN = function (x) {
                    as.list(x)
                  }), NULL)
}

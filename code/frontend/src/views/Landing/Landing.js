import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

const useStyles = makeStyles((theme) => ({
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
  }
}));

export default () => {

  const classes = useStyles();

  return (
    <main className={classes.content}>
      <div className={classes.toolbar} />
      
      <Typography variant="h3" component="h1">
        VideoStream
      </Typography>

      <img src={`${process.env.REACT_APP_API_URL}/video_feed`} alt="livestream of video camera"/>
    </main>
  )
}